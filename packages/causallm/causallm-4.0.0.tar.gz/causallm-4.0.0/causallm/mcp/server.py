"""MCP server implementation for CausalLLM."""

import asyncio
import uuid
from typing import Dict, Any, Optional, List
from causalllm.logging import get_logger
from .transport import MCPTransport, create_transport
from .tools import CausalTools
from .config import MCPConfig, load_mcp_config
from causalllm.llm_client import BaseLLMClient

logger = get_logger("causalllm.mcp.server")

class MCPServer:
    """MCP server for exposing CausalLLM functionality."""
    
    def __init__(self, config: Optional[MCPConfig] = None, llm_client: Optional[BaseLLMClient] = None):
        """Initialize MCP server with configuration."""
        logger.info("Initializing MCP server")
        
        self.config = config or load_mcp_config()
        self.transport: Optional[MCPTransport] = None
        self.tools = CausalTools(llm_client)
        self.client_info: Optional[Dict[str, Any]] = None
        self.server_info = {
            "name": self.config.server.name,
            "version": self.config.server.version,
            "description": self.config.server.description
        }
        self._running = False
        
        logger.info(f"MCP server initialized: {self.server_info['name']} v{self.server_info['version']}")
    
    async def start(self) -> None:
        """Start the MCP server."""
        logger.info("Starting MCP server")
        
        try:
            # Create transport
            self.transport = create_transport(
                transport_type=self.config.server.transport,
                host=self.config.server.host,
                port=self.config.server.port,
                message_handler=self._handle_message
            )
            
            # Start transport
            await self.transport.start()
            self._running = True
            
            logger.info(f"MCP server started on {self.config.server.transport}://{self.config.server.host}:{self.config.server.port}")
            
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            raise RuntimeError(f"Server startup failed: {e}")
    
    async def stop(self) -> None:
        """Stop the MCP server."""
        logger.info("Stopping MCP server")
        
        self._running = False
        
        if self.transport:
            await self.transport.stop()
            self.transport = None
        
        logger.info("MCP server stopped")
    
    async def _handle_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle incoming MCP messages."""
        try:
            method = message.get("method")
            msg_id = message.get("id")
            
            logger.debug(f"Handling MCP message: {method}")
            
            if method == "initialize":
                return await self._handle_initialize(message, msg_id)
            elif method == "ping":
                return await self._handle_ping(message, msg_id)
            elif method == "tools/list":
                return await self._handle_tools_list(message, msg_id)
            elif method == "tools/call":
                return await self._handle_tools_call(message, msg_id)
            elif method == "resources/list":
                return await self._handle_resources_list(message, msg_id)
            elif method == "prompts/list":
                return await self._handle_prompts_list(message, msg_id)
            else:
                logger.warning(f"Unknown method: {method}")
                return self._create_error_response(msg_id, -32601, f"Method not found: {method}")
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            return self._create_error_response(message.get("id"), -32603, f"Internal error: {str(e)}")
    
    async def _handle_initialize(self, message: Dict[str, Any], msg_id: str) -> Dict[str, Any]:
        """Handle MCP initialization."""
        logger.info("Handling MCP initialization")
        
        try:
            params = message.get("params", {})
            self.client_info = params.get("clientInfo", {})
            
            logger.info(f"Client connected: {self.client_info.get('name', 'Unknown')} v{self.client_info.get('version', 'Unknown')}")
            
            capabilities = {
                "tools": {
                    "listChanged": False  # We don't dynamically change tools
                },
                "resources": {
                    "subscribe": False,
                    "listChanged": False
                },
                "prompts": {
                    "listChanged": False
                },
                "logging": {}
            }
            
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": capabilities,
                    "serverInfo": self.server_info
                }
            }
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return self._create_error_response(msg_id, -32603, f"Initialization error: {str(e)}")
    
    async def _handle_ping(self, message: Dict[str, Any], msg_id: str) -> Dict[str, Any]:
        """Handle ping requests."""
        logger.debug("Handling ping")
        
        return {
            "jsonrpc": "2.0", 
            "id": msg_id,
            "result": {}
        }
    
    async def _handle_tools_list(self, message: Dict[str, Any], msg_id: str) -> Dict[str, Any]:
        """Handle tools list requests."""
        logger.debug("Handling tools list request")
        
        try:
            enabled_tools = self.config.tools.enabled_tools
            all_tools = self.tools.get_tool_list()
            
            # Filter to only enabled tools
            filtered_tools = [
                tool for tool in all_tools 
                if tool["name"] in enabled_tools
            ]
            
            logger.info(f"Returning {len(filtered_tools)} enabled tools")
            
            return {
                "jsonrpc": "2.0",
                "id": msg_id, 
                "result": {
                    "tools": filtered_tools
                }
            }
            
        except Exception as e:
            logger.error(f"Tools list failed: {e}")
            return self._create_error_response(msg_id, -32603, f"Tools list error: {str(e)}")
    
    async def _handle_tools_call(self, message: Dict[str, Any], msg_id: str) -> Dict[str, Any]:
        """Handle tool call requests."""
        params = message.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        logger.info(f"Handling tool call: {tool_name}")
        
        try:
            # Check if tool is enabled
            if tool_name not in self.config.tools.enabled_tools:
                return self._create_error_response(msg_id, -32601, f"Tool not enabled: {tool_name}")
            
            # Call the tool
            result = await self.tools.call_tool(tool_name, arguments)
            
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": result
            }
            
        except ValueError as e:
            logger.error(f"Invalid tool call: {e}")
            return self._create_error_response(msg_id, -32602, str(e))
        except Exception as e:
            logger.error(f"Tool call failed: {e}")
            return self._create_error_response(msg_id, -32603, f"Tool execution error: {str(e)}")
    
    async def _handle_resources_list(self, message: Dict[str, Any], msg_id: str) -> Dict[str, Any]:
        """Handle resources list requests."""
        logger.debug("Handling resources list request")
        
        # For now, we don't expose any resources
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "resources": []
            }
        }
    
    async def _handle_prompts_list(self, message: Dict[str, Any], msg_id: str) -> Dict[str, Any]:
        """Handle prompts list requests.""" 
        logger.debug("Handling prompts list request")
        
        # Expose some common causal reasoning prompts
        prompts = [
            {
                "name": "counterfactual_analysis",
                "description": "Template for counterfactual reasoning analysis",
                "arguments": [
                    {
                        "name": "context",
                        "description": "Background context",
                        "required": True
                    },
                    {
                        "name": "factual_scenario", 
                        "description": "What actually happened",
                        "required": True
                    },
                    {
                        "name": "counterfactual_change",
                        "description": "The hypothetical change to consider", 
                        "required": True
                    }
                ]
            },
            {
                "name": "causal_dag_analysis",
                "description": "Template for analyzing causal DAG structures",
                "arguments": [
                    {
                        "name": "variables",
                        "description": "List of variables in the system",
                        "required": True
                    },
                    {
                        "name": "relationships",
                        "description": "Causal relationships between variables",
                        "required": True
                    }
                ]
            },
            {
                "name": "treatment_effect_estimation",
                "description": "Template for treatment effect analysis",
                "arguments": [
                    {
                        "name": "treatment_description",
                        "description": "Description of the treatment",
                        "required": True
                    },
                    {
                        "name": "outcome_description", 
                        "description": "Description of the outcome",
                        "required": True
                    },
                    {
                        "name": "confounders",
                        "description": "Potential confounding variables",
                        "required": False
                    }
                ]
            }
        ]
        
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "prompts": prompts
            }
        }
    
    def _create_error_response(self, msg_id: Optional[str], code: int, message: str) -> Dict[str, Any]:
        """Create MCP error response."""
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {
                "code": code,
                "message": message
            }
        }
    
    async def run_forever(self) -> None:
        """Run the server forever (for stdio transport)."""
        logger.info("MCP server running...")
        
        try:
            while self._running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received interrupt, shutting down...")
        finally:
            await self.stop()

async def main():
    """Main entry point for running MCP server standalone."""
    import sys
    
    # Set up logging for standalone operation
    from causalllm.logging import setup_package_logging
    setup_package_logging(level="INFO", log_to_file=False)
    
    try:
        # Load configuration
        config_path = sys.argv[1] if len(sys.argv) > 1 else None
        config = load_mcp_config(config_path)
        
        # Create and start server
        server = MCPServer(config)
        await server.start()
        
        # Run forever
        await server.run_forever()
        
    except Exception as e:
        logger.error(f"Server failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())