# Production-Grade Customer Support AI Agent

An AI-powered customer support application built with **Amazon Bedrock AgentCore** and the **Strands Agents SDK**.

The project demonstrates how an AI agent can combine business operations, retrieval-augmented generation (RAG), persistent memory, code execution and browser interaction to deliver an integrated customer support experience.

## 1. Project Overview

The objective of this project was to develop a customer support AI agent capable of handling common customer service operations while maintaining conversational context and accessing external business capabilities.

The agent can:

- Retrieve customer and order information.
- Check refund eligibility and initiate refund requests.
- Answer product-related questions using a Knowledge Base.
- Retain customer preferences across interactions.
- Calculate loyalty rewards, discounts and order totals.
- Navigate web pages and retrieve relevant information.

The solution uses Amazon Bedrock AgentCore for agent deployment and managed capabilities, while the Strands Agents SDK provides the agent orchestration and tool integration.

## 2. System Architecture

The application separates the agent's reasoning from external business operations through AgentCore Gateway and MCP-connected tools.

### Architecture Components

| Component | Purpose |
|---|---|
| Amazon Bedrock | Provides the foundation model used by the agent. |
| Strands Agents SDK | Orchestrates the agent and its tools. |
| AgentCore Runtime | Hosts the deployed customer support agent. |
| AgentCore Gateway | Connects the agent to external business capabilities through MCP. |
| AWS Lambda | Implements order-tracking and refund-processing operations. |
| Amazon API Gateway | Exposes the order-management API. |
| Amazon Bedrock Knowledge Bases | Provides product and support information for retrieval-augmented responses. |
| AgentCore Memory | Stores and retrieves customer preferences and interaction history. |
| AgentCore Code Interpreter | Executes loyalty reward and discount calculations. |
| AgentCore Browser | Enables browser-based navigation and information retrieval. |

### Architecture Design

The agent communicates with external business tools through AgentCore Gateway.

Order-related operations are exposed through API Gateway and Lambda-backed functionality. Product information is retrieved through the Knowledge Base, while customer preferences are maintained through AgentCore Memory.

Code Interpreter handles loyalty calculations, and AgentCore Browser supports web interaction.

This modular design separates agent reasoning from the underlying business operations and makes individual capabilities easier to maintain and extend.

## 3. Core Features and Functional Testing

All six core capabilities were implemented and tested in the configured AWS environment.

### 3.1 Order Tracking

Retrieves customer and order information through Gateway-connected API tools.

The agent can provide:
- Order status.
- Product information.
- Shipping carrier.
- Tracking information.
- Estimated delivery information.

**Evidence:** `screenshots/functional/Deliverable_1_Order_Tracking.png`

### 3.2 Refund Processing

Connects to Lambda-backed refund-processing tools through AgentCore Gateway.

The agent can check refund status, retrieve return-label information and initiate refund requests.

**Evidence:** `screenshots/functional/Deliverable_2_Refund_Processing.png`

### 3.3 Knowledge Base and Retrieval-Augmented Generation

Uses Amazon Bedrock Knowledge Bases to retrieve relevant product and support information.

This enables the agent to provide responses grounded in retrieved information rather than relying exclusively on the foundation model's general knowledge.

**Evidence:** `screenshots/functional/Deliverable_3_Knowledge_Base_RAG.png`

### 3.4 Persistent Customer Memory

Uses AgentCore Memory to retain and retrieve customer preferences and interaction context.

This allows the agent to use previously established customer preferences when responding to subsequent interactions.

**Evidence:**
- `screenshots/functional/Deliverable_4_Memory_Persistence.png`
- `screenshots/functional/Deliverable_4_Memory_Persistence_Logs.png`

### 3.5 Loyalty Rewards Calculation

Uses AgentCore Code Interpreter to execute loyalty calculations.

The functionality includes:
- Loyalty-point redemption.
- Tier-based discounts.
- Final order total.
- Total customer savings.
- Points earned.
- Remaining loyalty points.

The application also validates the structured interpreter output before presenting calculation results.

**Evidence:**
- `screenshots/functional/Deliverable_5_Loyalty_Calculation.png`
- `screenshots/functional/Deliverable_5_Loyalty_Calculation_Logs.png`

### 3.6 Browser Interaction

Uses AgentCore Browser capabilities to navigate web pages and retrieve page information.

The implementation was tested using a successful browser navigation and page-content retrieval operation.

**Evidence:**
- `screenshots/functional/Deliverable_6_Browser_Interaction.png`
- `screenshots/functional/Deliverable_6_Browser_Interaction_Logs_1.png`
- `screenshots/functional/Deliverable_6_Browser_Interaction_Logs_2.png`
- `screenshots/functional/Deliverable_6_Browser_Interaction_Logs_3.png`

## 4. Technology Stack

### Programming and Agent Frameworks
- Python 3.13
- Strands Agents SDK
- MCP
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

### Development Tools
- uv
- Git
- Linux

## 5. Repository Structure

~~~text
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
~~~

### Important Files

| File | Description |
|---|---|
| `main.py` | Main agent implementation and orchestration. |
| `lambda/order_tracker.py` | Order-tracking Lambda implementation. |
| `lambda/refund_processor.py` | Refund-processing Lambda implementation. |
| `lambda/lambda_schema` | Lambda-related schema file. |
| `product_catalog.txt` | Product information used by the project. |
| `pyproject.toml` | Python project metadata and dependencies. |
| `uv.lock` | Locked dependency versions. |
| `REFLECTION.md` | Project reflection, technical challenges and lessons learned. |
| `screenshots/` | Functional and infrastructure evidence. |

## 6. Prerequisites

To work with this project, you need:

- Python 3.13.
- An AWS account with access to the required Amazon Bedrock and AgentCore services.
- AWS credentials configured through an appropriate credential provider.
- IAM permissions for the required AWS services.
- uv package manager.
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

~~~bash
export AWS_DEFAULT_REGION="us-east-1"
export GATEWAY_URL="<your-agentcore-gateway-mcp-endpoint>"
export KB_ID="<your-knowledge-base-id>"
export MEMORY_ID="<your-agentcore-memory-id>"
export MODEL_ID="amazon.nova-lite-v1:0"
~~~

An example environment template is provided in `.env.example`.

AWS credentials should be configured separately using an appropriate AWS credential provider. Do not place access keys, secret keys or other sensitive credentials in the repository.

## 8. Installation

Clone the repository:

~~~bash
git clone https://github.com/Light-Ibeh/production-grade-customer-support-ai-agent.git

cd production-grade-customer-support-ai-agent
~~~

Install project dependencies:

~~~bash
uv sync
~~~

Configure the required environment variables and AWS credentials before running or deploying the application.

## 9. Deployment

The application is deployed using the Amazon Bedrock AgentCore CLI.

With the required AWS infrastructure provisioned and the deployment configuration prepared, deploy the agent using:

~~~bash
uv run agentcore deploy
~~~

Check deployment status:

~~~bash
uv run agentcore status
~~~

The runtime should report a ready status before functional testing.

### Deployment Configuration Note

The local AgentCore deployment configuration is intentionally excluded from this repository because it contains environment-specific deployment settings.

Anyone deploying the project in another AWS environment must configure their own AgentCore resources, deployment settings, IAM permissions and environment variables.

The repository does not automatically provision all the AWS infrastructure required by the application.

## 10. Testing and Evidence

Functional testing was performed against the deployed AgentCore runtime.

The `screenshots/functional/` directory contains evidence for the six implemented capabilities.

The `screenshots/infrastructure/` directory contains additional evidence of infrastructure configuration and deployment.

### Infrastructure Evidence

| Evidence | File |
|---|---|
| IAM permission configuration | `IAM_Permission_Applied.png` |
| Knowledge Base configuration | `Infrastructure_1_Knowledge_Base.png` |
| AgentCore deployment | `Infrastructure_2_AgentCore_Deployment.png` |
| Runtime smoke test | `Smoke_Test_Success.png` |

CloudWatch log screenshots are also included where applicable to demonstrate tool execution and runtime behaviour.

## 11. Security Considerations

The repository excludes local AWS deployment state, environment-specific configuration, virtual environments and temporary files.

Security practices include:

- Supplying AWS credentials through secure credential providers.
- Using environment variables for resource identifiers.
- Excluding sensitive configuration from version control.
- Applying appropriate IAM permissions.
- Avoiding the publication of account-specific deployment information.

A production deployment should additionally implement stronger customer authentication, role-based access control, data-retention policies and approval workflows for sensitive operations.

## 12. Future Improvements

Potential improvements for a production environment include:

- Integrating a production order-management and payment system.
- Implementing stronger customer authentication and role-based access control.
- Introducing human approval for sensitive operations such as refunds.
- Expanding automated unit and integration testing.
- Improving error handling and application resilience.
- Introducing comprehensive usage and cost monitoring.
- Implementing more extensive security and data-retention controls.
- Replacing deprecated browser tooling with a supported integration using AgentCore BrowserClient.

## 13. Project Status

The customer support agent has been deployed to Amazon Bedrock AgentCore.

All six core functional capabilities have been successfully tested in the configured AWS environment:

1. Order tracking.
2. Refund processing.
3. Knowledge Base and RAG.
4. Persistent customer memory.
5. Loyalty rewards calculation.
6. Browser interaction.

Functional screenshots, infrastructure evidence and selected CloudWatch logs are included in this repository.

---

**Project:** Production-Grade Customer Support AI Agent
**Platform:** Amazon Bedrock AgentCore
**Agent Framework:** Strands Agents SDK
**Language:** Python 3.13
