"""
Customer Support AI Agent
Amazon Bedrock + Strands + AgentCore Runtime, Gateway/MCP,
Knowledge Base, Memory, Code Interpreter, and Browser.
AWS credentials are supplied by the Udacity lab environment.
"""

import argparse
import asyncio
import json
import logging
import os
import uuid
from typing import Any, Dict

import boto3
from strands import Agent, tool
from strands.models import BedrockModel
from strands.hooks import (
    HookProvider, AfterInvocationEvent, HookRegistry, MessageAddedEvent
)
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamable_http_client
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from bedrock_agentcore.memory import MemoryClient
from bedrock_agentcore.tools.code_interpreter_client import code_session
from strands_tools.browser import AgentCoreBrowser


# ============================================================
# CONFIGURATION
# ============================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CSAI_Agent")
os.environ.setdefault("BYPASS_TOOL_CONSENT", "true")

REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
GATEWAY_URL = os.getenv("GATEWAY_URL", "")
KB_ID = os.getenv("KB_ID", "")
MEMORY_ID = os.getenv("MEMORY_ID", "")
MODEL_ID = os.getenv("MODEL_ID", "amazon.nova-lite-v1:0")

app = BedrockAgentCoreApp()
model = BedrockModel(model_id=MODEL_ID, region_name=REGION)
memory_client = MemoryClient(region_name=REGION)
_bedrock_runtime = boto3.client(
    "bedrock-agent-runtime", region_name=REGION
)


# ============================================================
# MESSAGE AND MEMORY HELPERS
# ============================================================

def _plain_text(message: Any) -> str:
    if not isinstance(message, dict):
        return ""
    content = message.get("content", [])
    if isinstance(content, str):
        return content.strip()
    if not isinstance(content, list):
        return ""
    return "\n".join(
        block["text"]
        for block in content
        if isinstance(block, dict)
        and isinstance(block.get("text"), str)
    ).strip()


def _message_role(message: Any) -> str:
    return str(message.get("role", "")).lower() if isinstance(message, dict) else ""


def _memory_text(memory: Any) -> str:
    """Extract readable text from supported AgentCore Memory record shapes."""
    if isinstance(memory, str):
        return memory.strip()
    if not isinstance(memory, dict):
        return ""

    for key in ("content", "text", "memory", "value"):
        value = memory.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
        if isinstance(value, dict):
            nested = value.get("text") or value.get("value")
            if isinstance(nested, str) and nested.strip():
                return nested.strip()
        if isinstance(value, list):
            parts = [
                item.get("text", "")
                for item in value
                if isinstance(item, dict)
                and isinstance(item.get("text"), str)
            ]
            combined = "\n".join(
                part for part in parts if part.strip()
            ).strip()
            if combined:
                return combined
    return ""


# ============================================================
# AGENTCORE MEMORY
# ============================================================

def get_namespaces(
    mem_client: MemoryClient, memory_id: str
) -> Dict[str, str]:
    if not memory_id or memory_id.startswith("<"):
        return {}

    try:
        response = mem_client.get_memory_strategies(memory_id=memory_id)
    except TypeError:
        response = mem_client.get_memory_strategies(memory_id)

    if isinstance(response, list):
        strategies = response
    elif isinstance(response, dict):
        strategies = response.get(
            "memoryStrategies", response.get("strategies", [])
        )
    else:
        logger.warning(
            "Unexpected memory strategy response type: %s",
            type(response).__name__,
        )
        return {}

    namespaces = {}
    for item in strategies:
        if not isinstance(item, dict):
            continue
        strategy = item.get("strategy", item)
        if not isinstance(strategy, dict):
            continue

        kind = strategy.get("type") or strategy.get("strategyType")
        values = strategy.get("namespaces") or []
        if isinstance(values, str):
            values = [values]

        if not values:
            templates = strategy.get("namespaceTemplates") or []
            values = [
                (value.get("template") or value.get("namespace") or value)
                if isinstance(value, dict) else value
                for value in templates
            ]

        if kind and values:
            first = values[0]
            if isinstance(first, dict):
                first = first.get("template") or first.get("namespace")
            if isinstance(first, str):
                namespaces[str(kind)] = first

    logger.info("Memory namespaces discovered: %s", list(namespaces))
    return namespaces


class MemoryHook(HookProvider):
    def __init__(
        self,
        actor_id: str,
        session_id: str,
        memory_client: MemoryClient,
        memory_id: str,
    ):
        self.actor_id = actor_id
        self.session_id = session_id
        self.memory_client = memory_client
        self.memory_id = memory_id
        self.namespaces = get_namespaces(memory_client, memory_id)

    def retrieve_customer_context(self, event: MessageAddedEvent):
        if not self.memory_id or not self.namespaces:
            return

        messages = getattr(getattr(event, "agent", None), "messages", [])
        if not messages:
            return

        message = messages[-1]
        if _message_role(message) != "user":
            return

        query = _plain_text(message)
        if not query:
            return

        found = []
        for strategy_type, template in self.namespaces.items():
            namespace = (
                template.replace("{actorId}", self.actor_id)
                .replace("{actor_id}", self.actor_id)
            )
            try:
                response = self.memory_client.retrieve_memories(
                    memory_id=self.memory_id,
                    namespace=namespace,
                    query=query,
                    top_k=5,
                )
            except Exception as exc:
                logger.warning(
                    "Memory retrieval failed for %s: %s",
                    strategy_type,
                    exc,
                )
                continue

            # retrieve_memories can return a list directly or a wrapped dict.
            if isinstance(response, list):
                memories = response
            elif isinstance(response, dict):
                memories = response.get(
                    "memories", response.get("results", [])
                )
            else:
                memories = []

            if not isinstance(memories, list):
                logger.warning(
                    "Unexpected retrieved memory collection for %s: %s",
                    strategy_type,
                    type(memories).__name__,
                )
                continue

            for memory in memories:
                text = _memory_text(memory)
                if text:
                    found.append(f"[{strategy_type}] {text}")

        if found:
            enriched = (
                "Customer Context:\n"
                + "\n".join(found)
                + "\n\nCurrent customer message:\n"
                + query
            )
            message["content"] = (
                [{"text": enriched}]
                if isinstance(message.get("content"), list)
                else enriched
            )
            logger.info(
                "Injected %d retrieved memory record(s) for customer %s.",
                len(found),
                self.actor_id,
            )
        else:
            logger.info(
                "No relevant prior memories retrieved for customer %s.",
                self.actor_id,
            )

    def save_support_interaction(self, event: AfterInvocationEvent):
        if not self.memory_id:
            return

        messages = getattr(getattr(event, "agent", None), "messages", [])
        user_text = ""
        assistant_text = ""

        for message in reversed(messages or []):
            role = _message_role(message)
            text = _plain_text(message)
            if not text:
                continue
            if role == "assistant" and not assistant_text:
                assistant_text = text
            elif role == "user" and not user_text:
                user_text = text
            if user_text and assistant_text:
                break

        if not user_text or not assistant_text:
            logger.warning(
                "Memory event not saved: user or assistant message was missing."
            )
            return

        try:
            self.memory_client.create_event(
                memory_id=self.memory_id,
                actor_id=self.actor_id,
                session_id=self.session_id,
                messages=[
                    (user_text, "USER"),
                    (assistant_text, "ASSISTANT"),
                ],
            )
            logger.info(
                "Customer interaction saved to AgentCore Memory "
                "(actor=%s, session=%s).",
                self.actor_id,
                self.session_id,
            )
        except Exception as exc:
            logger.warning("Memory save failed: %s", exc)

    def register_hooks(self, registry: HookRegistry):
        registry.add_callback(
            MessageAddedEvent, self.retrieve_customer_context
        )
        registry.add_callback(
            AfterInvocationEvent, self.save_support_interaction
        )


# ============================================================
# KNOWLEDGE BASE
# ============================================================

@tool
def search_knowledge_base(query: str) -> str:
    """Search product specifications, return policies, warranties and store information."""
    if not KB_ID or KB_ID.startswith("<"):
        return "Knowledge Base is not configured. Do not invent policy information."
    try:
        response = _bedrock_runtime.retrieve(
            knowledgeBaseId=KB_ID,
            retrievalQuery={"text": query},
        )
        chunks = []
        for item in response.get("retrievalResults", []):
            content = item.get("content", {})
            text = (
                content.get("text", "")
                if isinstance(content, dict)
                else ""
            )
            if text:
                chunks.append(text)
        return "\n---\n".join(chunks) if chunks else (
            "No relevant information was found in the Knowledge Base."
        )
    except Exception as exc:
        logger.exception("Knowledge Base retrieval failed.")
        return (
            "Knowledge Base search is temporarily unavailable: "
            f"{type(exc).__name__}"
        )


# ============================================================
# CODE INTERPRETER OUTPUT PARSER
# ============================================================

_LOYALTY_FIELDS = {
    "points_redeemed",
    "points_discount",
    "tier_discount_pct",
    "tier_discount",
    "final_total",
    "total_savings",
    "points_earned",
    "remaining_points",
}


def _extract_code_interpreter_json(response: Any) -> Dict[str, Any]:
    """Parse structured JSON from the AgentCore Code Interpreter event stream."""
    if not isinstance(response, dict) or "stream" not in response:
        raise RuntimeError(
            "Code Interpreter response has no execution stream."
        )

    candidates = []
    errors = []

    for event in response["stream"]:
        if not isinstance(event, dict):
            continue
        result = event.get("result", {})
        if not isinstance(result, dict):
            continue

        if result.get("isError"):
            errors.append(
                "Code Interpreter marked execution as an error."
            )

        structured = result.get("structuredContent", {})
        if isinstance(structured, dict):
            exit_code = structured.get("exitCode")
            if exit_code not in (None, 0):
                errors.append(f"Code Interpreter exit code: {exit_code}")
            stdout = structured.get("stdout")
            if isinstance(stdout, str) and stdout.strip():
                candidates.append(stdout.strip())

        content = result.get("content", [])
        if isinstance(content, list):
            for part in content:
                if (
                    isinstance(part, dict)
                    and part.get("type") == "text"
                    and isinstance(part.get("text"), str)
                    and part["text"].strip()
                ):
                    candidates.append(part["text"].strip())

    if errors:
        raise RuntimeError(" ".join(errors))

    for candidate in candidates:
        candidate = candidate.strip()
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            left, right = candidate.find("{"), candidate.rfind("}")
            if left < 0 or right <= left:
                continue
            try:
                parsed = json.loads(candidate[left:right + 1])
            except json.JSONDecodeError:
                continue

        if (
            not isinstance(parsed, dict)
            or not _LOYALTY_FIELDS.issubset(parsed)
        ):
            continue

        for key in _LOYALTY_FIELDS:
            value = parsed[key]
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
            ):
                raise RuntimeError(
                    f"Invalid non-numeric interpreter value: {key}"
                )
        return parsed

    raise RuntimeError(
        "Execution stream did not contain the expected loyalty JSON."
    )


# ============================================================
# LOYALTY CALCULATION AND DETERMINISTIC FALLBACK
# ============================================================

def _calculate_tier_fallback(
    loyalty_points: int,
    tier: str,
    order_total: float,
    product_category: str,
) -> Dict[str, Any]:
    """Apply the same documented points and tier rules without Code Interpreter."""
    tier_rates = {
        "Silver": 0.00,
        "Gold": 0.10,
        "Platinum": 0.15,
    }
    earn_rates = {
        "standard": 1,
        "device": 2,
        "fresh": 5,
    }

    safe_tier = tier.title() if tier.title() in tier_rates else "Silver"
    safe_category = product_category.lower()
    points_balance = max(0, int(loyalty_points))
    total = max(0.0, float(order_total))

    requested_points = (points_balance // 500) * 500
    max_points_by_value = int((total * 0.50) * 100)
    max_points_by_value = (max_points_by_value // 500) * 500
    points_redeemed = min(requested_points, max_points_by_value)

    if points_redeemed < 500:
        points_redeemed = 0

    points_discount = points_redeemed / 100.0
    subtotal_after_points = max(0.0, total - points_discount)
    tier_discount_pct = tier_rates[safe_tier]
    tier_discount = round(
        subtotal_after_points * tier_discount_pct, 2
    )
    final_total = round(
        max(0.0, subtotal_after_points - tier_discount), 2
    )
    total_savings = round(total - final_total, 2)

    earn_rate = earn_rates.get(safe_category, 1)
    points_earned = int(final_total * earn_rate)
    remaining_points = (
        points_balance - points_redeemed + points_earned
    )

    return {
        "points_redeemed": points_redeemed,
        "points_discount": round(points_discount, 2),
        "tier_discount_pct": int(tier_discount_pct * 100),
        "tier_discount": tier_discount,
        "final_total": final_total,
        "total_savings": total_savings,
        "points_earned": points_earned,
        "remaining_points": remaining_points,
        "calculation_method": "tier_fallback",
        "calculation_completed": True,
    }


@tool
def calculate_loyalty_discount(
    loyalty_points: int,
    tier: str,
    order_total: float,
    product_category: str = "standard",
) -> str:
    """Calculate loyalty redemption and tier discount with Code Interpreter and a deterministic fallback."""
    safe_tier = (
        tier.title()
        if tier.title() in {"Silver", "Gold", "Platinum"}
        else "Silver"
    )
    safe_category = product_category.lower()
    loyalty_points = max(0, int(loyalty_points))
    order_total = max(0.0, float(order_total))

    code = f"""
import json
loyalty_points = {loyalty_points}
tier = {safe_tier!r}
order_total = {order_total!r}
product_category = {safe_category!r}
earn_rates = {{"standard": 1, "device": 2, "fresh": 5}}
tier_rates = {{"Silver": 0.00, "Gold": 0.10, "Platinum": 0.15}}
requested_points = (loyalty_points // 500) * 500
max_points_by_value = int((order_total * 0.50) * 100)
max_points_by_value = (max_points_by_value // 500) * 500
points_redeemed = min(requested_points, max_points_by_value)
if points_redeemed < 500:
    points_redeemed = 0
points_discount = points_redeemed / 100.0
subtotal_after_points = max(0.0, order_total - points_discount)
tier_discount_pct = tier_rates.get(tier, 0.0)
tier_discount = round(subtotal_after_points * tier_discount_pct, 2)
final_total = round(max(0.0, subtotal_after_points - tier_discount), 2)
total_savings = round(order_total - final_total, 2)
earn_rate = earn_rates.get(product_category, 1)
points_earned = int(final_total * earn_rate)
remaining_points = loyalty_points - points_redeemed + points_earned
print(json.dumps({{
    "points_redeemed": points_redeemed,
    "points_discount": round(points_discount, 2),
    "tier_discount_pct": int(tier_discount_pct * 100),
    "tier_discount": tier_discount,
    "final_total": final_total,
    "total_savings": total_savings,
    "points_earned": points_earned,
    "remaining_points": remaining_points
}}))
"""

    try:
        with code_session(REGION) as interpreter:
            response = interpreter.invoke(
                "executeCode",
                {
                    "code": code,
                    "language": "python",
                    "clearContext": True,
                },
            )

        calculation = _extract_code_interpreter_json(response)
        calculation["calculation_method"] = "code_interpreter"
        calculation["calculation_completed"] = True

        logger.info(
            "Code Interpreter loyalty calculation validated: %s",
            json.dumps(calculation, sort_keys=True),
        )
        return json.dumps(calculation, sort_keys=True)

    except Exception as exc:
        logger.exception(
            "Code Interpreter failed; using deterministic loyalty fallback."
        )
        fallback = _calculate_tier_fallback(
            loyalty_points=loyalty_points,
            tier=safe_tier,
            order_total=order_total,
            product_category=safe_category,
        )
        fallback["fallback_reason"] = type(exc).__name__
        logger.warning(
            "Loyalty fallback result: %s",
            json.dumps(fallback, sort_keys=True),
        )
        return json.dumps(fallback, sort_keys=True)


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are a professional customer support AI agent for a fictional online retail store.
You have access to live tools through Amazon Bedrock AgentCore Gateway and specialized tools.

MANDATORY TOOL EXECUTION:
Actually execute the appropriate tool for requests requiring live customer, order,
refund, policy, loyalty, or web data. Never merely describe an intended tool call.

ORDER TRACKING:
Use CustomerSupportOrderAPI___get_order with the supplied order_id.
Report only returned status, items, carrier, tracking number and ETA.
Do not ask for an ID already supplied or invent order information.

CUSTOMER INFORMATION:
Use CustomerSupportOrderAPI___get_customer for customer account information.
Use CustomerSupportOrderAPI___get_customer_orders for customer orders.
Supply the appropriate customer_id.

REFUNDS:
Use CustomerSupportRefundLambda___initiate_refund when order_id and reason are known.
Pass the order amount using the amount parameter whenever it is available from
the customer or a confirmed order lookup. Report approval only if the tool confirms it.
Use CustomerSupportRefundLambda___check_refund_status with refund_id for status checks.
Use CustomerSupportRefundLambda___get_return_label with order_id for return labels.
Never invent refund IDs, statuses, labels, or processing estimates.

KNOWLEDGE BASE:
Use search_knowledge_base for product specifications, return policies, warranties,
store policies, loyalty programme information and FAQs. Do not invent policies.
For membership-tier questions, search the Knowledge Base using the named tier
and the benefits requested by the customer.

LOYALTY:
Use calculate_loyalty_discount for all loyalty calculations.
Report points_redeemed, tier_discount_pct, final_total and remaining_points
from its returned JSON. Do not recalculate, modify, or guess these values.
The tool first attempts AgentCore Code Interpreter and uses a deterministic
tier fallback if the interpreter is unavailable. Both methods return calculated
values. Do not describe a successful fallback as a failed calculation.

BROWSER:
Use the browser tool when the customer requests information requiring live browsing.
For page-title requests, navigate to the exact supplied URL and report the
page title returned by the browser. Do not substitute another website.

GENERAL:
Never claim an action succeeded unless its tool confirms success.
Protect customer privacy. Be concise, professional and helpful.
If a tool fails, explain the failure honestly.
"""


# ============================================================
# AGENTCORE RUNTIME ENTRYPOINT
# ============================================================

@app.entrypoint
async def invoke(payload, context=None):
    """Handle one customer support request through AgentCore Runtime."""
    try:
        prompt = payload.get("prompt") or payload.get("user_input")
        if not prompt:
            return (
                "Please provide a customer support question "
                "in the prompt field."
            )

        actor_id = str(
            payload.get("customer_id")
            or payload.get("actor_id")
            or "anonymous"
        )
        session_id = str(payload.get("session_id") or uuid.uuid4())

        hooks = []
        if MEMORY_ID and not MEMORY_ID.startswith("<"):
            hooks = [
                MemoryHook(
                    actor_id,
                    session_id,
                    memory_client,
                    MEMORY_ID,
                )
            ]

        browser = AgentCoreBrowser(region=REGION)
        tools = [
            search_knowledge_base,
            calculate_loyalty_discount,
            browser.browser,
        ]

        if GATEWAY_URL and not GATEWAY_URL.startswith("<"):
            try:
                with MCPClient(
                    lambda: streamable_http_client(GATEWAY_URL)
                ) as mcp_client:
                    gateway_tools = mcp_client.list_tools_sync()
                    if not gateway_tools:
                        logger.error("Gateway returned no tools.")
                        return (
                            "Customer support tools are currently unavailable."
                        )

                    discovered_names = [
                        getattr(item, "tool_name", str(item))
                        for item in gateway_tools
                    ]
                    logger.info(
                        "Gateway tools discovered: %s",
                        discovered_names,
                    )
                    tools.extend(gateway_tools)
                    logger.info(
                        "Total agent tools registered: %d",
                        len(tools),
                    )

                    agent = Agent(
                        model=model,
                        tools=tools,
                        hooks=hooks,
                        system_prompt=SYSTEM_PROMPT,
                    )
                    response = await asyncio.to_thread(agent, prompt)

            except Exception as exc:
                logger.exception("Gateway or agent invocation failed.")
                return (
                    "The support agent could not complete the request "
                    f"({type(exc).__name__}). Please try again."
                )
        else:
            logger.warning("Gateway URL is not configured.")
            agent = Agent(
                model=model,
                tools=tools,
                hooks=hooks,
                system_prompt=SYSTEM_PROMPT,
            )
            response = await asyncio.to_thread(agent, prompt)

        if isinstance(response, str):
            return response

        content = (
            response.get("content", [])
            if isinstance(response, dict)
            else getattr(response, "content", [])
        )
        for block in content or []:
            if isinstance(block, dict) and block.get("text"):
                return block["text"]

        return str(response)

    except Exception as exc:
        logger.exception("Unhandled customer support agent error.")
        return (
            "The support agent encountered an error "
            f"({type(exc).__name__}). Please try again."
        )


# ============================================================
# LOCAL ENTRY POINT
# ============================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("payload", type=str)
    args = parser.parse_args()
    response = asyncio.run(invoke(json.loads(args.payload)))
    print(response)


if __name__ == "__main__":
    app.run()