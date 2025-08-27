"""MCP transport layer implementations."""

import asyncio
import json
import sys
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, Awaitable
from asyncio import StreamReader, StreamWriter
from causalllm.logging import get_logger

logger = get_logger("causalllm.mcp.transport")

class MCPTransport(ABC):
    """Abstract base class for MCP transport protocols."""
    
    def __init__(self, message_handler: Optional[Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]] = None):
        self.message_handler = message_handler
        self.is_connected = False
        
    @abstractmethod
    async def start(self) -> None:
        """Start the transport."""
        pass
    
    @abstractmethod 
    async def stop(self) -> None:
        """Stop the transport."""
        pass
    
    @abstractmethod
    async def send_message(self, message: Dict[str, Any]) -> None:
        """Send a message."""
        pass
    
    @abstractmethod
    async def receive_message(self) -> Dict[str, Any]:
        """Receive a message."""
        pass

class StdioTransport(MCPTransport):
    """Standard input/output transport for MCP."""
    
    def __init__(self, message_handler: Optional[Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]] = None):
        super().__init__(message_handler)
        self.reader: Optional[StreamReader] = None
        self.writer: Optional[StreamWriter] = None
        self._running = False
        
    async def start(self) -> None:
        """Start stdio transport."""
        logger.info("Starting stdio transport")
        
        try:
            # Create streams from stdin/stdout
            self.reader = asyncio.StreamReader()
            protocol = asyncio.StreamReaderProtocol(self.reader)
            
            # Connect to stdin
            loop = asyncio.get_event_loop()
            transport, _ = await loop.connect_read_pipe(lambda: protocol, sys.stdin)
            
            # Connect to stdout  
            _, self.writer = await loop.connect_write_pipe(
                lambda: asyncio.StreamWriter.transport, 
                sys.stdout
            )
            
            self.is_connected = True
            self._running = True
            
            logger.info("Stdio transport started successfully")
            
            # Start message loop if handler is provided
            if self.message_handler:
                await self._message_loop()
                
        except Exception as e:
            logger.error(f"Failed to start stdio transport: {e}")
            raise RuntimeError(f"Stdio transport startup failed: {e}")
    
    async def stop(self) -> None:
        """Stop stdio transport."""
        logger.info("Stopping stdio transport")
        
        self._running = False
        self.is_connected = False
        
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
            
        logger.info("Stdio transport stopped")
    
    async def send_message(self, message: Dict[str, Any]) -> None:
        """Send JSON message to stdout."""
        if not self.is_connected or not self.writer:
            raise RuntimeError("Transport not connected")
        
        try:
            json_data = json.dumps(message) + '\n'
            self.writer.write(json_data.encode('utf-8'))
            await self.writer.drain()
            
            logger.debug(f"Sent message: {message.get('method', 'response')}")
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise RuntimeError(f"Message send failed: {e}")
    
    async def receive_message(self) -> Dict[str, Any]:
        """Receive JSON message from stdin."""
        if not self.is_connected or not self.reader:
            raise RuntimeError("Transport not connected")
        
        try:
            line = await self.reader.readline()
            if not line:
                raise EOFError("Connection closed")
            
            message = json.loads(line.decode('utf-8').strip())
            logger.debug(f"Received message: {message.get('method', 'response')}")
            
            return message
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON received: {e}")
            raise ValueError(f"Invalid JSON message: {e}")
        except Exception as e:
            logger.error(f"Failed to receive message: {e}")
            raise RuntimeError(f"Message receive failed: {e}")
    
    async def _message_loop(self) -> None:
        """Main message processing loop."""
        logger.info("Starting stdio message loop")
        
        while self._running and self.is_connected:
            try:
                message = await self.receive_message()
                
                if self.message_handler:
                    response = await self.message_handler(message)
                    if response:
                        await self.send_message(response)
                        
            except EOFError:
                logger.info("Connection closed, stopping message loop")
                break
            except Exception as e:
                logger.error(f"Error in message loop: {e}")
                # Continue processing other messages

class WebSocketTransport(MCPTransport):
    """WebSocket transport for MCP."""
    
    def __init__(self, host: str = "localhost", port: int = 8000, 
                 message_handler: Optional[Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]] = None):
        super().__init__(message_handler)
        self.host = host
        self.port = port
        self.websocket = None
        self.server = None
        self._running = False
        
    async def start(self) -> None:
        """Start WebSocket transport as server."""
        logger.info(f"Starting WebSocket server on {self.host}:{self.port}")
        
        try:
            try:
                import websockets
            except ImportError as e:
                logger.error("WebSocket support requires 'websockets' package")
                raise ImportError("WebSocket transport requires 'websockets' package. Install with: pip install websockets") from e
                
            self.server = await websockets.serve(
                self._handle_connection,
                self.host,
                self.port
            )
            
            self._running = True
            logger.info(f"WebSocket server started on {self.host}:{self.port}")
            
        except Exception as e:
            logger.error(f"Failed to start WebSocket server: {e}")
            raise RuntimeError(f"WebSocket server startup failed: {e}")
    
    async def start_client(self, uri: str) -> None:
        """Start WebSocket transport as client."""
        logger.info(f"Connecting to WebSocket server at {uri}")
        
        try:
            try:
                import websockets
            except ImportError as e:
                logger.error("WebSocket support requires 'websockets' package")
                raise ImportError("WebSocket transport requires 'websockets' package. Install with: pip install websockets") from e
                
            self.websocket = await websockets.connect(uri)
            self.is_connected = True
            self._running = True
            
            logger.info(f"Connected to WebSocket server at {uri}")
            
            # Start message loop if handler is provided
            if self.message_handler:
                await self._message_loop()
                
        except Exception as e:
            logger.error(f"Failed to connect to WebSocket server: {e}")
            raise RuntimeError(f"WebSocket client connection failed: {e}")
    
    async def stop(self) -> None:
        """Stop WebSocket transport."""
        logger.info("Stopping WebSocket transport")
        
        self._running = False
        self.is_connected = False
        
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.server = None
            
        logger.info("WebSocket transport stopped")
    
    async def send_message(self, message: Dict[str, Any]) -> None:
        """Send JSON message via WebSocket."""
        if not self.is_connected or not self.websocket:
            raise RuntimeError("WebSocket not connected")
        
        try:
            json_data = json.dumps(message)
            await self.websocket.send(json_data)
            
            logger.debug(f"Sent WebSocket message: {message.get('method', 'response')}")
            
        except Exception as e:
            logger.error(f"Failed to send WebSocket message: {e}")
            raise RuntimeError(f"WebSocket message send failed: {e}")
    
    async def receive_message(self) -> Dict[str, Any]:
        """Receive JSON message via WebSocket."""
        if not self.is_connected or not self.websocket:
            raise RuntimeError("WebSocket not connected")
        
        try:
            data = await self.websocket.recv()
            message = json.loads(data)
            
            logger.debug(f"Received WebSocket message: {message.get('method', 'response')}")
            return message
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON received via WebSocket: {e}")
            raise ValueError(f"Invalid JSON message: {e}")
        except Exception as e:
            logger.error(f"Failed to receive WebSocket message: {e}")
            raise RuntimeError(f"WebSocket message receive failed: {e}")
    
    async def _handle_connection(self, websocket, path):
        """Handle incoming WebSocket connection."""
        logger.info(f"New WebSocket connection from {websocket.remote_address}")
        
        self.websocket = websocket
        self.is_connected = True
        
        try:
            async for message_data in websocket:
                try:
                    message = json.loads(message_data)
                    
                    if self.message_handler:
                        response = await self.message_handler(message)
                        if response:
                            await self.send_message(response)
                            
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON from WebSocket client: {e}")
                    error_response = {
                        "jsonrpc": "2.0", 
                        "error": {"code": -32700, "message": "Parse error"},
                        "id": None
                    }
                    await self.send_message(error_response)
                    
        except Exception as conn_closed:
            # Check if this is a websockets connection closed exception
            if 'ConnectionClosed' in str(type(conn_closed)):
                logger.info("WebSocket connection closed")
            else:
                logger.error(f"WebSocket connection error: {conn_closed}")
        finally:
            self.is_connected = False
            self.websocket = None
    
    async def _message_loop(self) -> None:
        """Main message processing loop for client."""
        logger.info("Starting WebSocket message loop")
        
        while self._running and self.is_connected:
            try:
                message = await self.receive_message()
                
                if self.message_handler:
                    response = await self.message_handler(message)
                    if response:
                        await self.send_message(response)
                        
            except Exception as conn_closed:
                if 'ConnectionClosed' in str(type(conn_closed)):
                    logger.info("WebSocket connection closed, stopping message loop")
                    break
                else:
                    logger.error(f"WebSocket message loop error: {conn_closed}")
                    break
            except Exception as e:
                logger.error(f"Error in WebSocket message loop: {e}")

class HTTPTransport(MCPTransport):
    """HTTP transport for MCP (future implementation)."""
    
    def __init__(self, host: str = "localhost", port: int = 8000,
                 message_handler: Optional[Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]] = None):
        super().__init__(message_handler)
        self.host = host
        self.port = port
        
    async def start(self) -> None:
        """Start HTTP transport (placeholder)."""
        logger.info("HTTP transport not yet implemented")
        raise NotImplementedError("HTTP transport coming soon")
    
    async def stop(self) -> None:
        """Stop HTTP transport (placeholder).""" 
        pass
    
    async def send_message(self, message: Dict[str, Any]) -> None:
        """Send HTTP message (placeholder)."""
        raise NotImplementedError("HTTP transport coming soon")
    
    async def receive_message(self) -> Dict[str, Any]:
        """Receive HTTP message (placeholder)."""
        raise NotImplementedError("HTTP transport coming soon")

def create_transport(transport_type: str, **kwargs) -> MCPTransport:
    """Factory function to create transport instances."""
    logger.info(f"Creating {transport_type} transport")
    
    if transport_type.lower() == "stdio":
        return StdioTransport(**kwargs)
    elif transport_type.lower() == "websocket":
        return WebSocketTransport(**kwargs)
    elif transport_type.lower() == "http":
        return HTTPTransport(**kwargs)
    else:
        raise ValueError(f"Unsupported transport type: {transport_type}")