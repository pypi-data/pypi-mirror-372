"""
WebSocket protocol handler for real-time bidirectional communication.
Provides async WebSocket server and client implementations with stream processing integration.
"""

import asyncio
import json
import time
import logging
from typing import Optional, Callable, Dict, Any, Set, Union, AsyncIterator
from dataclasses import dataclass, field
from urllib.parse import urlparse
import ssl

logger = logging.getLogger(__name__)

# Optional websockets import
try:
    import websockets
    from websockets.server import WebSocketServerProtocol
    from websockets.client import WebSocketClientProtocol
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    WebSocketServerProtocol = None
    WebSocketClientProtocol = None
    logger.info("websockets not available, WebSocket functionality disabled")


@dataclass
class WebSocketConfig:
    """Configuration for WebSocket connections."""
    host: str = "localhost"
    port: int = 8765
    path: str = "/"
    ping_interval: Optional[float] = 20.0
    ping_timeout: Optional[float] = 20.0
    close_timeout: Optional[float] = 10.0
    max_size: Optional[int] = 2**20  # 1MB
    max_queue: Optional[int] = 32
    compression: Optional[str] = None
    ssl_context: Optional[ssl.SSLContext] = None
    extra_headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class WebSocketMessage:
    """WebSocket message wrapper."""
    data: Union[str, bytes]
    message_type: str = "text"  # text, binary, json
    timestamp: float = field(default_factory=time.time)
    client_id: Optional[str] = None
    
    def to_json(self) -> str:
        """Convert message to JSON string."""
        if self.message_type == "json":
            return json.dumps(self.data)
        elif self.message_type == "text":
            return json.dumps({
                "data": self.data,
                "type": self.message_type,
                "timestamp": self.timestamp,
                "client_id": self.client_id
            })
        else:
            raise ValueError("Cannot convert binary message to JSON")


class WebSocketHandler:
    """Base WebSocket handler with stream processing integration."""
    
    def __init__(self, config: Optional[WebSocketConfig] = None):
        self.config = config or WebSocketConfig()
        self.clients: Set = set()
        self._message_handlers: Dict[str, Callable] = {}
        self._stream_processor = None
        self.is_running = False
    
    def set_stream_processor(self, processor):
        """Set stream processor for message processing."""
        self._stream_processor = processor
    
    def register_message_handler(self, message_type: str, handler: Callable[[WebSocketMessage], Any]) -> None:
        """Register a handler for specific message types."""
        self._message_handlers[message_type] = handler
    
    async def handle_message(self, websocket, message: str) -> None:
        """Handle incoming WebSocket message."""
        try:
            # Try to parse as JSON
            try:
                data = json.loads(message)
                msg_type = data.get("type", "json")
                ws_message = WebSocketMessage(
                    data=data.get("data", data),
                    message_type=msg_type,
                    client_id=str(id(websocket))
                )
            except json.JSONDecodeError:
                # Plain text message
                ws_message = WebSocketMessage(
                    data=message,
                    message_type="text",
                    client_id=str(id(websocket))
                )
            
            # Process with stream processor if available
            if self._stream_processor and hasattr(self._stream_processor, 'process_chunks'):
                results = list(self._stream_processor.process_chunks(
                    ws_message.data, "websocket_handler"
                ))
                for result in results:
                    await self.send_to_client(websocket, result)
            
            # Handle with registered handlers
            handler = self._message_handlers.get(ws_message.message_type)
            if handler:
                result = await self._call_handler(handler, ws_message)
                if result:
                    await self.send_to_client(websocket, result)
                    
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
            await self.send_error(websocket, str(e))
    
    async def _call_handler(self, handler: Callable, message: WebSocketMessage) -> Any:
        """Call handler function, supporting both sync and async handlers."""
        if asyncio.iscoroutinefunction(handler):
            return await handler(message)
        else:
            return handler(message)
    
    async def send_to_client(self, websocket, data: Any) -> None:
        """Send data to specific client."""
        try:
            if isinstance(data, dict):
                await websocket.send(json.dumps(data))
            else:
                await websocket.send(str(data))
        except Exception as e:
            logger.error(f"Error sending to client: {e}")
    
    async def send_error(self, websocket, error_message: str) -> None:
        """Send error message to client."""
        error_data = {
            "type": "error",
            "message": error_message,
            "timestamp": time.time()
        }
        await self.send_to_client(websocket, error_data)
    
    async def broadcast(self, data: Any, exclude: Optional[Set] = None) -> None:
        """Broadcast data to all connected clients."""
        exclude = exclude or set()
        disconnected = set()
        
        for client in self.clients:
            if client in exclude:
                continue
                
            try:
                await self.send_to_client(client, data)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.add(client)
        
        # Remove disconnected clients
        self.clients -= disconnected


class WebSocketServer(WebSocketHandler):
    """WebSocket server implementation."""
    
    def __init__(self, config: Optional[WebSocketConfig] = None):
        super().__init__(config)
        self.server = None
    
    async def client_handler(self, websocket, path: str) -> None:
        """Handle new client connection."""
        self.clients.add(websocket)
        client_id = str(id(websocket))
        logger.info(f"Client {client_id} connected from {websocket.remote_address}")
        
        try:
            # Send welcome message
            welcome = {
                "type": "welcome",
                "client_id": client_id,
                "timestamp": time.time()
            }
            await self.send_to_client(websocket, welcome)
            
            # Handle messages
            async for message in websocket:
                await self.handle_message(websocket, message)
                
        except Exception as e:
            logger.error(f"Client {client_id} error: {e}")
        finally:
            self.clients.remove(websocket)
            logger.info(f"Client {client_id} disconnected")
    
    async def start_server(self) -> None:
        """Start the WebSocket server."""
        if not WEBSOCKETS_AVAILABLE:
            raise RuntimeError("websockets library not available")
        
        logger.info(f"Starting WebSocket server on {self.config.host}:{self.config.port}")
        
        self.server = await websockets.serve(
            self.client_handler,
            self.config.host,
            self.config.port,
            ping_interval=self.config.ping_interval,
            ping_timeout=self.config.ping_timeout,
            close_timeout=self.config.close_timeout,
            max_size=self.config.max_size,
            max_queue=self.config.max_queue,
            compression=self.config.compression,
            ssl=self.config.ssl_context,
            extra_headers=self.config.extra_headers
        )
        
        self.is_running = True
        logger.info("WebSocket server started successfully")
    
    async def stop_server(self) -> None:
        """Stop the WebSocket server."""
        if self.server:
            logger.info("Stopping WebSocket server")
            self.server.close()
            await self.server.wait_closed()
            self.is_running = False
            logger.info("WebSocket server stopped")
    
    async def run_forever(self) -> None:
        """Run the server until interrupted."""
        await self.start_server()
        try:
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            logger.info("Server interrupted by user")
        finally:
            await self.stop_server()


class WebSocketClient(WebSocketHandler):
    """WebSocket client implementation."""
    
    def __init__(self, uri: str, config: Optional[WebSocketConfig] = None):
        super().__init__(config)
        self.uri = uri
        self.websocket: Optional = None
        self._receive_task: Optional[asyncio.Task] = None
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 5
        self._reconnect_delay = 1.0
    
    async def connect(self) -> None:
        """Connect to WebSocket server."""
        if not WEBSOCKETS_AVAILABLE:
            raise RuntimeError("websockets library not available")
        
        logger.info(f"Connecting to WebSocket server at {self.uri}")
        
        try:
            self.websocket = await websockets.connect(
                self.uri,
                ping_interval=self.config.ping_interval,
                ping_timeout=self.config.ping_timeout,
                close_timeout=self.config.close_timeout,
                max_size=self.config.max_size,
                max_queue=self.config.max_queue,
                compression=self.config.compression,
                ssl=self.config.ssl_context,
                extra_headers=self.config.extra_headers
            )
            
            self.is_running = True
            self._reconnect_attempts = 0
            logger.info("Connected to WebSocket server")
            
            # Start message receiving task
            self._receive_task = asyncio.create_task(self._receive_messages())
            
        except Exception as e:
            logger.error(f"Failed to connect to WebSocket server: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from WebSocket server."""
        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass
        
        if self.websocket:
            logger.info("Disconnecting from WebSocket server")
            await self.websocket.close()
            self.websocket = None
            self.is_running = False
            logger.info("Disconnected from WebSocket server")
    
    async def _receive_messages(self) -> None:
        """Receive messages from server."""
        try:
            async for message in self.websocket:
                await self.handle_message(self.websocket, message)
        except Exception as e:
            logger.error(f"Error receiving messages: {e}")
            if self.is_running:
                await self._attempt_reconnect()
    
    async def _attempt_reconnect(self) -> None:
        """Attempt to reconnect to server."""
        if self._reconnect_attempts >= self._max_reconnect_attempts:
            logger.error("Max reconnection attempts reached")
            return
        
        self._reconnect_attempts += 1
        delay = self._reconnect_delay * (2 ** (self._reconnect_attempts - 1))
        
        logger.info(f"Attempting to reconnect in {delay:.1f} seconds (attempt {self._reconnect_attempts})")
        await asyncio.sleep(delay)
        
        try:
            await self.connect()
        except Exception as e:
            logger.error(f"Reconnection attempt {self._reconnect_attempts} failed: {e}")
    
    async def send_message(self, data: Any) -> None:
        """Send message to server."""
        if not self.websocket or not self.is_running:
            raise RuntimeError("Not connected to server")
        
        try:
            if isinstance(data, dict):
                await self.websocket.send(json.dumps(data))
            else:
                await self.websocket.send(str(data))
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            if self.is_running:
                await self._attempt_reconnect()
    
    async def send_json(self, data: Dict[str, Any]) -> None:
        """Send JSON message to server."""
        await self.send_message(data)
    
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self.websocket is not None and self.is_running