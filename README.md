# Production-Grade Customer Support AI Agent

An AI-powered customer support application built with **Amazon Bedrock AgentCore** and the **Strands Agents SDK**.

The project demonstrates how an AI agent can combine business operations, retrieval-augmented generation (RAG), persistent customer memory, code execution, and browser interaction in a single customer-support workflow.

## 1. Project Overview

The agent is designed to handle common customer-service operations while maintaining conversational context and accessing external business capabilities.

It can:

- Retrieve customer and order information.
- Check refund information and initiate refund requests.
- Answer product and loyalty-program questions using a Knowledge Base.
- Retain customer preferences across separate conversations.
- Calculate loyalty-point redemptions, tier discounts, order totals, and earned points.
- Navigate web pages and retrieve page information.

Amazon Bedrock AgentCore provides the managed runtime and agent capabilities. The Strands Agents SDK provides agent orchestration and tool integration.

## 2. System Architecture

The application separates agent reasoning from external business operations through AgentCore Gateway and MCP-connected tools.

### Architecture Components

| Component | Purpose |
|---|---|
| Amazon Bedrock | Provides the foundation model used by the agent. |
| Strands Agents SDK | Orchestrates the agent and its tools. |
| AgentCore Runtime | Hosts the deployed customer-support agent. |
| AgentCore Gateway | Connects the agent to external business capabilities through MCP. |
| AWS Lambda | Implements order-tracking and refund-processing operations. |
| Amazon API Gateway | Exposes the order-management API. |
| Amazon Bedrock Knowledge Bases | Retrieves product and support information. |
| AgentCore Memory | Stores and retrieves customer preferences and interaction history. |
| AgentCore Code Interpreter | Executes loyalty-reward and discount calculations. |
| AgentCore Browser | Enables browser-based navigation and information retrieval. |

### Architecture Design

The agent accesses order and refund operations through Gateway-connected tools. Product and loyalty information is retrieved through the Knowledge Base, while AgentCore Memory makes customer preferences available across interactions.

Code Interpreter performs loyalty calculations. AgentCore Browser supports web navigation and page-content retrieval.

This modular design separates agent reasoning from backend business operations and makes individual capabilities easier to maintain and extend.

## 3. Core Features and Functional Testing

The six core capabilities were exercised against the deployed AgentCore runtime. The following sections describe the tests performed and link to the corresponding evidence.

### 3.1 Order Tracking

Order information is retrieved through Gateway-connected API tools.

The agent can provide:

- Order status.
- Product information.
- Shipping carrier.
- Tracking information.
- Estimated delivery information.

**Evidence:** `screenshots/functional/Deliverable_1_Order_Tracking.png`

### 3.2 Refund Processing

Refund operations are connected to Lambda-backed tools through AgentCore Gateway.

The agent can retrieve refund information and initiate refund requests using the available business tools.

**Evidence:** `screenshots/functional/Deliverable_2_Refund_Processing.png`

### 3.3 Knowledge Base and Retrieval-Augmented Generation

Amazon Bedrock Knowledge Bases retrieves relevant product and loyalty-program information to ground the agent's responses.

**Reviewer test:** The agent was asked to explain the benefits and privileges available to Platinum loyalty members. The response included free same-day shipping, a 15% tier discount, priority customer support, points-earning rules, redemption rules, and loyalty-tier thresholds. CloudWatch logs confirmed invocation of the `search_knowledge_base` tool.

**Evidence:**

- `screenshots/functional/Deliverable_3_Knowledge_Base_RAG.png`
- `screenshots/functional/Deliverable_3_Knowledge_Base_Command.png`
- `screenshots/functional/Deliverable_3_Knowledge_Base_Response_1.png`
- `screenshots/functional/Deliverable_3_Knowledge_Base_Response_2.png`
- `screenshots/functional/Deliverable_3_Knowledge_Base_Verification_Log.png`

### 3.4 Persistent Customer Memory

AgentCore Memory stores and retrieves customer preferences and interaction context.

**Reviewer test:** In the first session, a test customer named Jane asked the agent to remember that product recommendations should compare price, warranty, and return policy. In a separate second session, Jane asked what criteria should be used. The agent recalled all three preferences without Jane repeating them. Runtime logs confirmed that memory records were retrieved and injected into the second session.

**Evidence:**

- `screenshots/functional/Deliverable_4_Memory_Persistence.png`
- `screenshots/functional/Deliverable_4_Memory_Persistence_Logs.png`
- `screenshots/functional/Memory_Jane_Session1_Preference_Saved.png`
- `screenshots/functional/Memory_Jane_Session1_Response.png`
- `screenshots/functional/Memory_Jane_Session2_Retrieval_Command.png`
- `screenshots/functional/Memory_Jane_Session2_Preference_Recalled.png`
- `screenshots/functional/Memory_CloudWatch_Retrieval_Verification.png`

### 3.5 Loyalty Rewards Calculation

AgentCore Code Interpreter executes the loyalty calculation. The application parses and validates the structured calculation output before presenting the result.

**Reviewer test inputs:**

| Input | Value |
|---|---:|
| Loyalty points | 4,250 |
| Membership tier | Gold |
| Order total | $150.00 |
| Product category | Standard |

**Verified calculation:**

| Result | Value |
|---|---:|
| Points redeemed | 4,000 |
| Points discount | $40.00 |
| Gold tier discount | 10% |
| Tier discount amount | $11.00 |
| Final order total | $99.00 |
| Total savings | $51.00 |
| Points earned | 99 |
| Remaining points | 349 |

The test response identified `code_interpreter` as the calculation method.

**Evidence:**

- `screenshots/functional/Deliverable_5_Loyalty_Calculation.png`
- `screenshots/functional/Deliverable_5_Loyalty_Calculation_Logs.png`
- `screenshots/functional/Deliverable_4_Loyalty_Gold_Calculation_Command.png`
- `screenshots/functional/Deliverable_4_Loyalty_Gold_Calculation.png`

### 3.6 Browser Interaction

AgentCore Browser is used to navigate web pages and retrieve page information.

**Reviewer test:** The agent was asked to visit `https://www.udacity.com` and report the page title. It returned:

`Learn the Latest Tech Skills; Advance Your Career | Udacity`

The response was obtained and the runtime logs recorded browser tool activity, session initialization, and successful invocation completion. The logs also showed asynchronous browser execution warnings during the attempt, so browser reliability remains an area for improvement.

**Evidence:**

- `screenshots/functional/Deliverable_6_Browser_Interaction.png`
- `screenshots/functional/Deliverable_6_Browser_Interaction_Logs_1.png`
- `screenshots/functional/Deliverable_6_Browser_Interaction_Logs_2.png`
- `screenshots/functional/Deliverable_6_Browser_Interaction_Logs_3.png`
- `screenshots/functional/Browser_01_Udacity_Test_Command.png`
- `screenshots/functional/Browser_02_Udacity_Page_Title.png`
- `screenshots/functional/Browser_03_CloudWatch_Tool_Invocation.png`
- `screenshots/functional/Browser_04_CloudWatch_Session_Started.png`
- `screenshots/functional/Browser_05_CloudWatch_Invocation_Completed.png`

## 4. Technology Stack

### Programming and Agent Frameworks

- Python 3.13
- Strands Agents SDK
- Model Context Protocol (MCP)
- Boto3

### AWS Services

- Amazon Bedrock
- Amazon Bedrock AgentCore Runtime
- Amazon Bedrock AgentCore Gateway
- Amazon Bedrock AgentCore Memory
- Amazon Bedrock AgentCore Code Interpreter
- Amazon Bedrock AgentCore Browser
- Amazon Bedrock Knowledge Bases
- AWS Lambda
- Amazon API Gateway
- Amazon CloudWatch

### Development Tools

- uv
- Git
- Linux
- Visual Studio Code

## 5. Repository Structure

```text
.
├── lambda/
│   ├── lambda_schema
│   ├── order_tracker.py
│   └── refund_processor.py
├── screenshots/
│   ├── functional/
│   └── infrastructure/
├── main.py
├── product_catalog.txt
├── pyproject.toml
├── uv.lock
├── README.md
├── REFLECTION.md
├── .env.example
└── .gitignore
```

### Important Files

| File | Description |
|---|---|
| `main.py` | Main agent implementation, orchestration, and tool integration. |
| `lambda/order_tracker.py` | Order-tracking Lambda implementation. |
| `lambda/refund_processor.py` | Refund-processing Lambda implementation. |
| `lambda/lambda_schema` | Lambda-related schema file. |
| `product_catalog.txt` | Product information used by the project. |
| `pyproject.toml` | Python project metadata and dependencies. |
| `uv.lock` | Locked dependency versions. |
| `REFLECTION.md` | Project reflection, technical challenges, and lessons learned. |
| `screenshots/` | Functional test and infrastructure evidence. |

## 6. Prerequisites

To work with this project, you need:

- Python 3.13.
- An AWS account with access to the required Amazon Bedrock and AgentCore services.
- AWS credentials configured through an appropriate credential provider.
- IAM permissions for the required AWS services.
- The uv package manager.
- Access to the required AgentCore and Knowledge Base resources.

## 7. Configuration

The application uses environment variables to configure its AWS resources and model.

| Variable | Description | Default |
|---|---|---|
| `AWS_DEFAULT_REGION` | AWS deployment region. | `us-east-1` |
| `GATEWAY_URL` | AgentCore Gateway MCP endpoint. | Required |
| `KB_ID` | Bedrock Knowledge Base ID. | Required |
| `MEMORY_ID` | AgentCore Memory ID. | Required |
| `MODEL_ID` | Bedrock foundation model ID. | `amazon.nova-lite-v1:0` |

### Example Configuration

```bash
export AWS_DEFAULT_REGION="us-east-1"
export GATEWAY_URL="<your-agentcore-gateway-mcp-endpoint>"
export KB_ID="<your-knowledge-base-id>"
export MEMORY_ID="<your-agentcore-memory-id>"
export MODEL_ID="amazon.nova-lite-v1:0"
```

An example environment template is provided in `.env.example`.

AWS credentials should be configured separately using an appropriate AWS credential provider. Do not place access keys, secret keys, or other sensitive credentials in the repository.

## 8. Installation

Clone the repository:

```bash
git clone https://github.com/Light-Ibeh/production-grade-customer-support-ai-agent.git
cd production-grade-customer-support-ai-agent
```

Install project dependencies:

```bash
uv sync
```

Configure the required environment variables and AWS credentials before running or deploying the application.

## 9. Deployment

The application is deployed using the Amazon Bedrock AgentCore CLI.

With the required AWS infrastructure provisioned and deployment configuration prepared, deploy the agent using:

```bash
uv run agentcore deploy
```

Check deployment status:

```bash
uv run agentcore status
```

The runtime should report a ready status before functional testing.

### Deployment Configuration Note

The local AgentCore deployment configuration is intentionally excluded from this repository because it contains environment-specific deployment settings.

Anyone deploying the project in another AWS environment must configure their own AgentCore resources, deployment settings, IAM permissions, and environment variables. The repository does not automatically provision all AWS infrastructure required by the application.

## 10. Testing and Evidence

Functional testing was performed against the deployed AgentCore runtime. The `screenshots/functional/` directory contains the original feature evidence and the additional reviewer-focused test evidence. The `screenshots/infrastructure/` directory contains infrastructure and deployment evidence.

### Infrastructure Evidence

| Evidence | File |
|---|---|
| IAM permission configuration | `screenshots/infrastructure/IAM_Permission_Applied.png` |
| Knowledge Base configuration | `screenshots/infrastructure/Infrastructure_1_Knowledge_Base.png` |
| AgentCore deployment | `screenshots/infrastructure/Infrastructure_2_AgentCore_Deployment.png` |
| Runtime smoke test | `screenshots/infrastructure/Smoke_Test_Success.png` |
| Deployment success | `screenshots/infrastructure/deployment_success.png` |
| Runtime status | `screenshots/infrastructure/runtime_status.png` |

CloudWatch log screenshots are included where applicable to demonstrate tool execution, memory retrieval, and runtime behaviour.

## 11. Security Considerations

The repository excludes local AWS deployment state, environment-specific configuration, virtual environments, and temporary files.

Security practices include:

- Supplying AWS credentials through secure credential providers.
- Using environment variables for resource identifiers.
- Excluding sensitive configuration from version control.
- Applying appropriate IAM permissions.
- Avoiding publication of account-specific deployment information.

A production deployment should additionally implement stronger customer authentication, role-based access control, data-retention policies, and approval workflows for sensitive operations.

## 12. Future Improvements

Potential improvements for a production environment include:

- Integrating a production order-management and payment system.
- Implementing stronger customer authentication and role-based access control.
- Introducing human approval for sensitive operations such as refunds.
- Protecting refund operations with idempotency controls to prevent duplicate transactions on retries.
- Expanding automated unit and integration testing.
- Improving browser reliability by replacing deprecated browser tooling with a supported integration using AgentCore BrowserClient and Playwright.
- Introducing comprehensive usage and cost monitoring.
- Implementing more extensive security and data-retention controls.

## 13. Project Status

The customer-support agent has been deployed to Amazon Bedrock AgentCore. The six core capabilities have been exercised in the configured AWS environment:

1. Order tracking.
2. Refund processing.
3. Knowledge Base retrieval.
4. Persistent customer memory across separate sessions.
5. Loyalty rewards calculation using Code Interpreter.
6. Browser navigation and page-title retrieval.

The repository includes the original functional evidence, additional reviewer-focused screenshots, infrastructure evidence, and the project reflection.

---

**Project:** Production-Grade Customer Support AI Agent
**Platform:** Amazon Bedrock AgentCore
**Agent Framework:** Strands Agents SDK
**Language:** Python 3.13
