"""MCP client implementation for CausalLLM."""

import asyncio
import uuid
from typing import Dict, Any, Optional, List
from ..utils.logging import get_logger
from .transport import MCPTransport, create_transport
from .config import MCPConfig, load_mcp_config

logger = get_logger("causalllm.mcp.client")

class MCPClient:
    """MCP client for connecting to CausalLLM servers."""
    
    def __init__(self, config: Optional[MCPConfig] = None):
        """Initialize MCP client with configuration."""
        logger.info("Initializing MCP client")
        
        self.config = config or load_mcp_config()
        self.transport: Optional[MCPTransport] = None
        self.server_info: Optional[Dict[str, Any]] = None
        self.server_capabilities: Optional[Dict[str, Any]] = None
        self._connected = False
        self._request_counter = 0
        
        logger.info("MCP client initialized")
    
    async def connect(self) -> None:
        """Connect to MCP server."""
        logger.info(f"Connecting to MCP server: {self.config.client.server_name}")
        
        try:
            # Create transport
            if self.config.client.transport == "stdio":
                self.transport = create_transport("stdio")
            elif self.config.client.transport == "websocket":
                self.transport = create_transport(
                    "websocket",
                    host=self.config.client.host,
                    port=self.config.client.port
                )
            else:
                raise ValueError(f"Unsupported client transport: {self.config.client.transport}")
            
            # Start transport
            if self.config.client.transport == "websocket":
                uri = f"ws://{self.config.client.host}:{self.config.client.port}"
                await self.transport.start_client(uri)
            else:
                await self.transport.start()
            
            # Initialize connection
            await self._initialize()
            
            self._connected = True
            logger.info("Successfully connected to MCP server")
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            raise RuntimeError(f"MCP connection failed: {e}")
    
    async def disconnect(self) -> None:
        """Disconnect from MCP server."""
        logger.info("Disconnecting from MCP server")
        
        self._connected = False
        
        if self.transport:
            await self.transport.stop()
            self.transport = None
        
        logger.info("Disconnected from MCP server")
    
    async def _initialize(self) -> None:
        """Initialize MCP connection."""
        logger.debug("Initializing MCP connection")
        
        # Send initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "initialize", 
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {
                        "listChanged": False
                    },
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "causalllm-client",
                    "version": "1.0.0"
                }
            }
        }
        
        response = await self._send_request(init_request)
        
        if "error" in response:
            raise RuntimeError(f"Initialization failed: {response['error']['message']}")
        
        result = response.get("result", {})
        self.server_info = result.get("serverInfo", {})
        self.server_capabilities = result.get("capabilities", {})
        
        logger.info(f"Connected to server: {self.server_info.get('name', 'Unknown')} v{self.server_info.get('version', 'Unknown')}")
    
    async def ping(self) -> bool:
        """Ping the server to check connection."""
        if not self._connected:
            return False
        
        try:
            request = {
                "jsonrpc": "2.0",
                "id": self._next_request_id(),
                "method": "ping"
            }
            
            response = await self._send_request(request)
            return "result" in response
            
        except Exception as e:
            logger.error(f"Ping failed: {e}")
            return False
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from server."""
        logger.debug("Requesting tool list")
        
        if not self._connected:
            raise RuntimeError("Not connected to MCP server")
        
        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/list"
        }
        
        response = await self._send_request(request)
        
        if "error" in response:
            raise RuntimeError(f"Tools list failed: {response['error']['message']}")
        
        tools = response.get("result", {}).get("tools", [])
        logger.info(f"Received {len(tools)} tools from server")
        
        return tools
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the server."""
        logger.info(f"Calling tool: {name}")
        
        if not self._connected:
            raise RuntimeError("Not connected to MCP server")
        
        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments
            }
        }
        
        response = await self._send_request(request)
        
        if "error" in response:
            error = response["error"]
            raise RuntimeError(f"Tool call failed: {error['message']} (code: {error['code']})")
        
        result = response.get("result", {})
        logger.info(f"Tool {name} completed successfully")
        
        return result
    
    async def list_resources(self) -> List[Dict[str, Any]]:
        """List available resources from server."""
        logger.debug("Requesting resource list")
        
        if not self._connected:
            raise RuntimeError("Not connected to MCP server")
        
        request = {
            "jsonrpc": "2.0", 
            "id": self._next_request_id(),
            "method": "resources/list"
        }
        
        response = await self._send_request(request)
        
        if "error" in response:
            raise RuntimeError(f"Resources list failed: {response['error']['message']}")
        
        resources = response.get("result", {}).get("resources", [])
        logger.info(f"Received {len(resources)} resources from server")
        
        return resources
    
    async def list_prompts(self) -> List[Dict[str, Any]]:
        """List available prompts from server.""" 
        logger.debug("Requesting prompt list")
        
        if not self._connected:
            raise RuntimeError("Not connected to MCP server")
        
        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(), 
            "method": "prompts/list"
        }
        
        response = await self._send_request(request)
        
        if "error" in response:
            raise RuntimeError(f"Prompts list failed: {response['error']['message']}")
        
        prompts = response.get("result", {}).get("prompts", [])
        logger.info(f"Received {len(prompts)} prompts from server")
        
        return prompts
    
    async def _send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send request and wait for response."""
        if not self.transport:
            raise RuntimeError("Transport not available")
        
        try:
            # Send request
            await self.transport.send_message(request)
            
            # Wait for response
            response = await self.transport.receive_message()
            
            return response
            
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise RuntimeError(f"MCP request failed: {e}")
    
    def _next_request_id(self) -> str:
        """Generate next request ID."""
        self._request_counter += 1
        return f"req-{self._request_counter}"
    
    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._connected

# Convenience client for LLM integration
class MCPLLMClient:
    """LLM client that uses MCP for causal reasoning capabilities."""
    
    def __init__(self, mcp_config: Optional[MCPConfig] = None):
        """Initialize MCP-based LLM client.""" 
        self.mcp_client = MCPClient(mcp_config)
        self._connected = False
        
    async def connect(self) -> None:
        """Connect to MCP server."""
        await self.mcp_client.connect()
        self._connected = True
        
    async def disconnect(self) -> None:
        """Disconnect from MCP server."""
        await self.mcp_client.disconnect()
        self._connected = False
    
    async def simulate_counterfactual(self, context: str, factual: str, intervention: str, 
                                    instruction: Optional[str] = None, temperature: float = 0.7,
                                    chain_of_thought: bool = False) -> str:
        """Simulate counterfactual via MCP."""
        if not self._connected:
            raise RuntimeError("Not connected to MCP server")
            
        args = {
            "context": context,
            "factual": factual,
            "intervention": intervention,
            "temperature": temperature,
            "chain_of_thought": chain_of_thought
        }
        
        if instruction:
            args["instruction"] = instruction
            
        result = await self.mcp_client.call_tool("simulate_counterfactual", args)
        
        # Extract text from MCP response
        content = result.get("content", [])
        if content and content[0].get("type") == "text":
            return content[0].get("text", "")
        else:
            return "No response received"
    
    async def generate_do_prompt(self, context: str, variables: Dict[str, str], 
                               intervention: Dict[str, str], question: Optional[str] = None) -> str:
        """Generate do-calculus prompt via MCP."""
        if not self._connected:
            raise RuntimeError("Not connected to MCP server")
            
        args = {
            "context": context,
            "variables": variables,
            "intervention": intervention
        }
        
        if question:
            args["question"] = question
            
        result = await self.mcp_client.call_tool("generate_do_prompt", args)
        
        # Extract text from MCP response
        content = result.get("content", [])
        if content and content[0].get("type") == "text":
            return content[0].get("text", "")
        else:
            return "No response received"
    
    async def extract_causal_edges(self, scenario_description: str, model: str = "gpt-4", 
                                 temperature: float = 0.3) -> List[tuple]:
        """Extract causal edges via MCP."""
        if not self._connected:
            raise RuntimeError("Not connected to MCP server")
            
        args = {
            "scenario_description": scenario_description,
            "model": model, 
            "temperature": temperature
        }
        
        result = await self.mcp_client.call_tool("extract_causal_edges", args)
        
        # Return raw edges data if available
        return result.get("edges", [])

async def main():
    """Example usage of MCP client.""" 
    import sys
    
    # Set up logging
    from ..utils.logging import setup_package_logging
    setup_package_logging(level="INFO", log_to_file=False)
    
    try:
        # Create client
        client = MCPClient()
        await client.connect()
        
        # List available tools
        tools = await client.list_tools()
        print(f"Available tools: {[t['name'] for t in tools]}")
        
        # Example tool call
        result = await client.call_tool("simulate_counterfactual", {
            "context": "A person is deciding whether to take an umbrella",
            "factual": "It started raining and the person got wet",
            "intervention": "The person took an umbrella"
        })
        
        print(f"Result: {result}")
        
        await client.disconnect()
        
    except Exception as e:
        logger.error(f"Client example failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())