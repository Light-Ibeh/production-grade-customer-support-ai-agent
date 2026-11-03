# Project Reflection: Building a Production-Grade Customer Support AI Agent

Building this project involved several technical challenges and important architectural decisions. One key decision was to use Amazon Bedrock AgentCore Gateway with MCP to connect the agent to external business capabilities, including order tracking and refund processing through AWS Lambda. Although direct Lambda integration could have reduced the initial setup complexity, I chose Gateway because it provides centralized tool discovery, separates the agent's reasoning from backend business logic, and makes the architecture easier to extend and maintain. I also implemented AgentCore Memory to retain customer preferences and interaction history, alongside a Knowledge Base for retrieving product information.

## Technical Challenges and Resolutions

One of the most challenging aspects was troubleshooting the integration between AgentCore Gateway and the order management API. The initial Gateway target failed because the exported OpenAPI specification lacked required response definitions and operation identifiers. I resolved this by correcting the API method responses, redeploying the API, and updating the existing Gateway target.

Another challenge involved parsing Code Interpreter responses. Although the interpreter executed the loyalty calculation successfully, the application initially failed to extract the structured output correctly. I investigated the response structure, updated the parser to process streaming responses, and introduced validation to improve calculation reliability.

I also encountered differences in AgentCore Memory retrieval response formats. I updated the application to handle both list-based and dictionary-based responses, then verified that customer preferences persisted across separate sessions through a two-session test.

## Production Considerations

For a production environment, I would strengthen authentication and role-based access control, integrate a real order management and payment system, and introduce human approval for sensitive operations such as refunds. For example, refund requests should be validated against the original order amount and protected with idempotency keys to prevent duplicate transactions when requests are retried.

I would also add automated integration tests, usage and cost monitoring, comprehensive security and data-retention controls, and stronger error handling. Finally, I would replace the deprecated browser tooling with a supported custom integration using AgentCore BrowserClient and Playwright to improve browser reliability.
