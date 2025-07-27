// This is a placeholder for the full bundled content of the MCP SDK.
// In a real scenario, you would download the file from a reliable source like unpkg:
// https://unpkg.com/@modelcontextprotocol/sdk/dist/mcp.js
// For this environment, we'll simulate the core functionality.

window.mcp = (() => {
  // This is a simplified mock of the SDK for demonstration.
  // A real implementation would be thousands of lines long.

  class Client {
    constructor(options) {
      this.name = options.name;
      this.version = options.version;
      this.transport = null;
      this.tools = {};
      console.log(`MCP Client '${this.name}' created.`);
    }

    async connect(transport) {
      this.transport = transport;
      console.log("Attempting to connect via transport...");
      // In a real SDK, this would establish a connection and get a list of tools.
      // We will mock the tools we know the server has.
      this.tools.judge = {
        validate_move: (params) => this.transport.callTool('judge', 'validate_move', params),
      };
      this.tools.opponent = {
         get_opponent_move: (params) => this.transport.callTool('opponent', 'get_opponent_move', params),
      };
       this.tools.advisor = {
         get_advice: (params) => this.transport.callTool('advisor', 'get_advice', params),
      };
      console.log("Mock connection successful. Tools are available.");
      return Promise.resolve();
    }
  }

  class StreamableHTTPClientTransport {
    constructor(baseUrl) {
      this.baseUrl = baseUrl;
      console.log(`HTTP Transport initialized for URL: ${baseUrl}`);
    }

    async callTool(protocol, toolName, params) {
        const toolUrl = new URL(`${this.baseUrl.pathname}${protocol}/tools/${toolName}`, this.baseUrl.origin);
        console.log(`Calling tool at: ${toolUrl}`);
        
        const response = await fetch(toolUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });

        if (!response.ok) {
            throw new Error(`Tool call failed with status: ${response.status}`);
        }
        
        const data = await response.json();
        // The python server wraps the result, so we extract it.
        return data.result;
    }
  }

  return { Client, StreamableHTTPClientTransport };
})();
