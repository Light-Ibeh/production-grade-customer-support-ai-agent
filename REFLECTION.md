# Project Reflection: Building a Production-Grade Customer Support AI Agent

## Project Experience

Building this customer support AI agent provided an opportunity to apply cloud engineering, AI integration and troubleshooting skills in a practical AWS environment.

One of my key architectural decisions was using Amazon Bedrock AgentCore Gateway with MCP to connect the agent to external business capabilities. These included order tracking and refund processing through AWS Lambda. This approach separated the agent's reasoning from the underlying business logic, making the solution more modular and maintainable.

I also integrated AgentCore Memory to retain customer preferences and interaction history, alongside a Knowledge Base for retrieving relevant product information. Additional capabilities included loyalty reward calculations through Code Interpreter and browser-based interactions.

## Technical Challenges and Solutions

### 1. AgentCore Gateway Integration

One of the most challenging aspects was troubleshooting the integration between AgentCore Gateway and the order management API.

The initial Gateway target failed because the exported OpenAPI specification lacked required response definitions and operation identifiers.

I resolved this by correcting the API method responses, redeploying the API and updating the existing Gateway target. This restored the connection between the agent and its external business tools.

### 2. Code Interpreter Response Parsing

Another significant challenge involved extracting structured results from the Code Interpreter response.

Although the interpreter successfully executed the loyalty calculations, the application initially failed to extract and interpret the returned output correctly.

I investigated the streaming response structure, updated the parser to process the returned events and introduced validation to ensure the calculations were accurate before presenting the results to customers.

### 3. Deployment and Environment Troubleshooting

The deployment process also required troubleshooting environment compatibility, AWS credentials, dependencies and AgentCore runtime configuration.

Working through these issues improved my understanding of AWS service integration, runtime deployment and cloud-based debugging.

## Key Lessons Learned

- Designing modular AI applications requires clear separation between agent reasoning and external business operations.
- MCP provides a structured approach to connecting agents with external tools.
- Successful tool execution does not automatically guarantee correct application-level response handling.
- Structured output validation is important when an AI agent performs calculations or business operations.
- Cloud deployment requires careful attention to permissions, environment configuration and observability.
- CloudWatch logs are valuable for tracing tool execution and diagnosing runtime issues.

## Future Improvements

For a production environment, I would:

- Implement stronger authentication and role-based access control.
- Integrate a real order-management and payment system.
- Introduce human approval for sensitive operations such as refunds.
- Expand automated unit and integration testing.
- Improve error handling and resilience.
- Introduce comprehensive usage and cost monitoring.
- Implement stronger security and data-retention controls.
- Replace deprecated browser tooling with a supported integration using AgentCore BrowserClient.

## Conclusion

This project strengthened my practical understanding of building and deploying AI-powered applications on AWS. It also demonstrated how cloud infrastructure, agent orchestration, external tools, persistent memory and knowledge retrieval can work together to deliver a more capable customer support experience.
