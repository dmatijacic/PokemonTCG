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
        validate_setup: (params) => this.transport.callTool('judge', 'validate_setup', params),
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
      // ISPRAVAK: Osigurajmo da bazni URL uvijek ima kosu crtu na kraju
      this.baseUrl = baseUrl.href.endsWith('/') ? baseUrl.href : `${baseUrl.href}/`;
      console.log(`HTTP Transport initialized for URL: ${this.baseUrl}`);
    }

    async callTool(protocol, toolName, params) {
        // ISPRAVAK: Jednostavnija i sigurnija konstrukcija URL-a
        const toolUrl = new URL(`${protocol}/tools/${toolName}`, this.baseUrl);
        console.log(`Calling tool at: ${toolUrl}`);
        
        const response = await fetch(toolUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error("Tool call failed with status:", response.status, "and message:", errorText);
            throw new Error(`Tool call failed with status: ${response.status}`);
        }
        
        const data = await response.json();
        return data.result;
    }
  }

  return { Client, StreamableHTTPClientTransport };
})();
