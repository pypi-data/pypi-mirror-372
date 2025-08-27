"""MCP configuration management for CausalLLM."""

import os
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path
from ..utils.logging import get_logger

logger = get_logger("causalllm.mcp.config")

@dataclass
class MCPServerConfig:
    """Configuration for MCP server."""
    name: str = "causalllm-server"
    version: str = "1.0.0"
    description: str = "CausalLLM MCP Server for causal reasoning"
    transport: str = "stdio"  # stdio, websocket, http
    host: str = "localhost"
    port: int = 8000
    max_connections: int = 10
    timeout: int = 30
    log_level: str = "INFO"

@dataclass  
class MCPClientConfig:
    """Configuration for MCP client."""
    server_name: str
    transport: str = "stdio"  # stdio, websocket, http
    host: str = "localhost"
    port: int = 8000
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0

@dataclass
class MCPToolConfig:
    """Configuration for MCP tools."""
    enabled_tools: List[str] = None
    tool_timeout: int = 60
    max_prompt_length: int = 10000
    enable_streaming: bool = False
    
    def __post_init__(self):
        if self.enabled_tools is None:
            self.enabled_tools = [
                "simulate_counterfactual",
                "generate_do_prompt", 
                "extract_causal_edges",
                "generate_reasoning_prompt",
                "analyze_treatment_effect"
            ]

@dataclass
class MCPConfig:
    """Main MCP configuration container."""
    server: MCPServerConfig = None
    client: MCPClientConfig = None
    tools: MCPToolConfig = None
    
    def __post_init__(self):
        if self.server is None:
            self.server = MCPServerConfig()
        if self.client is None:
            self.client = MCPClientConfig(server_name="causalllm-server")
        if self.tools is None:
            self.tools = MCPToolConfig()

    @classmethod
    def from_file(cls, config_path: str) -> 'MCPConfig':
        """Load configuration from JSON file."""
        logger.info(f"Loading MCP config from: {config_path}")
        
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
            
            # Parse nested configurations
            server_config = MCPServerConfig(**data.get('server', {}))
            client_config = MCPClientConfig(**data.get('client', {'server_name': 'causalllm-server'}))
            tools_config = MCPToolConfig(**data.get('tools', {}))
            
            config = cls(
                server=server_config,
                client=client_config, 
                tools=tools_config
            )
            
            logger.info("MCP configuration loaded successfully")
            return config
            
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return cls()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise ValueError(f"Invalid configuration file: {e}")
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise RuntimeError(f"Configuration loading failed: {e}")

    @classmethod
    def from_env(cls) -> 'MCPConfig':
        """Load configuration from environment variables."""
        logger.info("Loading MCP config from environment variables")
        
        # Server config from env
        server_config = MCPServerConfig(
            name=os.getenv("MCP_SERVER_NAME", "causalllm-server"),
            version=os.getenv("MCP_SERVER_VERSION", "1.0.0"),
            transport=os.getenv("MCP_TRANSPORT", "stdio"),
            host=os.getenv("MCP_HOST", "localhost"),
            port=int(os.getenv("MCP_PORT", "8000")),
            max_connections=int(os.getenv("MCP_MAX_CONNECTIONS", "10")),
            timeout=int(os.getenv("MCP_TIMEOUT", "30")),
            log_level=os.getenv("MCP_LOG_LEVEL", "INFO")
        )
        
        # Client config from env  
        client_config = MCPClientConfig(
            server_name=os.getenv("MCP_CLIENT_SERVER", "causalllm-server"),
            transport=os.getenv("MCP_CLIENT_TRANSPORT", "stdio"),
            host=os.getenv("MCP_CLIENT_HOST", "localhost"),
            port=int(os.getenv("MCP_CLIENT_PORT", "8000")),
            timeout=int(os.getenv("MCP_CLIENT_TIMEOUT", "30"))
        )
        
        # Tools config from env
        enabled_tools_env = os.getenv("MCP_ENABLED_TOOLS")
        enabled_tools = enabled_tools_env.split(",") if enabled_tools_env else None
        
        tools_config = MCPToolConfig(
            enabled_tools=enabled_tools,
            tool_timeout=int(os.getenv("MCP_TOOL_TIMEOUT", "60")),
            max_prompt_length=int(os.getenv("MCP_MAX_PROMPT_LENGTH", "10000"))
        )
        
        return cls(
            server=server_config,
            client=client_config,
            tools=tools_config
        )

    def to_file(self, config_path: str) -> None:
        """Save configuration to JSON file."""
        logger.info(f"Saving MCP config to: {config_path}")
        
        try:
            # Ensure directory exists
            Path(config_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to dict and save
            data = {
                'server': asdict(self.server),
                'client': asdict(self.client),
                'tools': asdict(self.tools)
            }
            
            with open(config_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.info("MCP configuration saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            raise RuntimeError(f"Configuration saving failed: {e}")

    def validate(self) -> None:
        """Validate configuration settings."""
        logger.debug("Validating MCP configuration")
        
        # Validate server config
        if self.server.transport not in ["stdio", "websocket", "http"]:
            raise ValueError(f"Invalid transport: {self.server.transport}")
        
        if self.server.port < 1 or self.server.port > 65535:
            raise ValueError(f"Invalid port: {self.server.port}")
            
        if self.server.max_connections < 1:
            raise ValueError(f"Invalid max_connections: {self.server.max_connections}")
        
        # Validate client config
        if self.client.transport not in ["stdio", "websocket", "http"]:
            raise ValueError(f"Invalid client transport: {self.client.transport}")
            
        if self.client.retry_attempts < 0:
            raise ValueError(f"Invalid retry_attempts: {self.client.retry_attempts}")
        
        # Validate tools config
        valid_tools = {
            "simulate_counterfactual",
            "generate_do_prompt",
            "extract_causal_edges", 
            "generate_reasoning_prompt",
            "analyze_treatment_effect"
        }
        
        for tool in self.tools.enabled_tools:
            if tool not in valid_tools:
                logger.warning(f"Unknown tool enabled: {tool}")
        
        if self.tools.tool_timeout < 1:
            raise ValueError(f"Invalid tool_timeout: {self.tools.tool_timeout}")
            
        logger.info("MCP configuration validation passed")

def load_mcp_config(config_path: Optional[str] = None) -> MCPConfig:
    """
    Load MCP configuration from file or environment.
    
    Args:
        config_path: Optional path to config file. If not provided, uses environment.
        
    Returns:
        MCPConfig instance
    """
    if config_path:
        config = MCPConfig.from_file(config_path)
    else:
        # Try default locations
        default_paths = [
            "mcp_config.json",
            "config/mcp.json", 
            os.path.expanduser("~/.causalllm/mcp_config.json"),
            "/etc/causalllm/mcp_config.json"
        ]
        
        config = None
        for path in default_paths:
            if os.path.exists(path):
                config = MCPConfig.from_file(path)
                break
        
        # Fallback to environment variables
        if config is None:
            config = MCPConfig.from_env()
    
    # Validate configuration
    config.validate()
    
    return config