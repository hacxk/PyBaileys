import asyncio
import logging
from typing import Any, Callable, Dict, Optional, Union
from urllib.parse import urlparse

import websockets
from websockets.exceptions import WebSocketException

from .abstract_socket_client import AbstractSocketClient
from defaults.defaults import DEFAULT_ORIGIN, SocketConfig

logger = logging.getLogger(__name__)

class WebSocketClient(AbstractSocketClient):
    def __init__(self, url: str, config: SocketConfig):
        super().__init__(url, config)
        self.socket: Optional[websockets.WebSocketClientProtocol] = None
        self.ping_interval: float = config.ping_interval or 20.0
        self.ping_timeout: float = config.ping_timeout or 10.0
        self.pong_timeout: float = config.pong_timeout or 10.0
        self.reconnect_interval: float = config.reconnect_interval or 5.0
        self.max_reconnect_attempts: int = config.max_reconnect_attempts or 5
        self.ping_task: Optional[asyncio.Task] = None
        self.reconnect_task: Optional[asyncio.Task] = None
        self.event_handlers: Dict[str, list] = {}
        self.close_code: Optional[int] = None
        self.close_reason: Optional[str] = None

    @property
    def is_open(self) -> bool:
        return self.socket is not None and self.socket.open

    @property
    def is_closed(self) -> bool:
        return self.socket is None or self.socket.closed

    @property
    def is_closing(self) -> bool:
        return self.socket is None or self.socket.closing

    @property
    def is_connecting(self) -> bool:
        return self.socket is not None and not self.socket.open and not self.socket.closed

    async def connect(self) -> None:
        if self.socket:
            return

        parsed_url = urlparse(self.url)
        ssl_context = None
        if parsed_url.scheme == "wss":
            import ssl
            ssl_context = ssl.create_default_context()

        try:
            self.socket = await websockets.connect(
                self.url,
                origin=DEFAULT_ORIGIN,
                extra_headers=self.config.options.get('headers', {}),
                open_timeout=self.config.connect_timeout_ms / 1000,
                close_timeout=self.config.connect_timeout_ms / 1000,
                ping_interval=None,  # We'll handle pings manually
                ping_timeout=None,
                ssl=ssl_context
            )

            logger.info(f"Connected to WebSocket at {self.url}")
            self.emit('open')

            # Emit 'upgrade' event
            self.emit('upgrade', self.socket.response_headers)

            # Start the ping task
            self.ping_task = asyncio.create_task(self._ping_loop())

            # Start the message handler
            asyncio.create_task(self._message_handler())

        except WebSocketException as e:
            logger.error(f"Failed to connect to WebSocket: {e}")
            self.emit('error', e)
            await self._handle_connection_failure()

    async def close(self) -> None:
        if not self.socket:
            return

        if self.ping_task:
            self.ping_task.cancel()
            self.ping_task = None

        try:
            await self.socket.close()
        except WebSocketException as e:
            logger.error(f"Error closing WebSocket: {e}")
            self.emit('error', e)
        finally:
            self.socket = None
            self.emit('close', self.close_code, self.close_reason)

    async def send(self, data: Union[str, bytes]) -> bool:
        if not self.socket or not self.is_open:
            logger.warning("Attempted to send message on closed WebSocket")
            return False

        try:
            await self.socket.send(data)
            self.emit('sent', data)
            return True
        except WebSocketException as e:
            logger.error(f"Error sending message: {e}")
            self.emit('error', e)
            return False

    async def ping(self, data: Optional[Union[str, bytes]] = None) -> None:
        if self.socket and self.is_open:
            try:
                await self.socket.ping(data)
                self.emit('ping', data)
            except WebSocketException as e:
                logger.error(f"Error sending ping: {e}")
                self.emit('error', e)

    async def pong(self, data: Optional[Union[str, bytes]] = None) -> None:
        if self.socket and self.is_open:
            try:
                await self.socket.pong(data)
                self.emit('pong', data)
            except WebSocketException as e:
                logger.error(f"Error sending pong: {e}")
                self.emit('error', e)

    async def _ping_loop(self) -> None:
        while self.is_open:
            await asyncio.sleep(self.ping_interval)
            try:
                ping_start = asyncio.get_event_loop().time()
                await self.ping(b'keepalive')
                pong_waiter = await self.socket.ping()
                await asyncio.wait_for(pong_waiter, timeout=self.pong_timeout)
                ping_duration = asyncio.get_event_loop().time() - ping_start
                self.emit('latency', ping_duration)
            except asyncio.TimeoutError:
                logger.warning("Pong timeout")
                self.emit('error', Exception("Pong timeout"))
                await self.close()
                break
            except Exception as e:
                logger.error(f"Error in ping loop: {e}")
                self.emit('error', e)
                await self.close()
                break

    async def _message_handler(self) -> None:
        while self.is_open:
            try:
                message = await self.socket.recv()
                self.emit('message', message)
            except websockets.ConnectionClosed as e:
                self.close_code = e.code
                self.close_reason = e.reason
                logger.info(f"WebSocket closed: code={e.code}, reason={e.reason}")
                await self.close()
                break
            except Exception as e:
                logger.error(f"Error in message handler: {e}")
                self.emit('error', e)
                await self.close()
                break

    async def _handle_connection_failure(self) -> None:
        if self.reconnect_task and not self.reconnect_task.done():
            return

        self.reconnect_task = asyncio.create_task(self._reconnect_loop())

    async def _reconnect_loop(self) -> None:
        attempts = 0
        while attempts < self.max_reconnect_attempts:
            logger.info(f"Attempting to reconnect (attempt {attempts + 1}/{self.max_reconnect_attempts})")
            await asyncio.sleep(self.reconnect_interval)
            try:
                await self.connect()
                if self.is_open:
                    logger.info("Reconnection successful")
                    self.emit('reconnect')
                    break
            except Exception as e:
                logger.error(f"Reconnection attempt failed: {e}")
            attempts += 1

        if not self.is_open:
            logger.error("Max reconnection attempts reached")
            self.emit('reconnect_failed')

    def on(self, event: str, callback: Callable[..., Any]) -> None:
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(callback)

    def off(self, event: str, callback: Callable[..., Any]) -> None:
        if event in self.event_handlers:
            self.event_handlers[event] = [cb for cb in self.event_handlers[event] if cb != callback]

    def emit(self, event: str, *args: Any) -> None:
        if event in self.event_handlers:
            for callback in self.event_handlers[event]:
                asyncio.create_task(self._safe_callback(callback, *args))

    async def _safe_callback(self, callback: Callable[..., Any], *args: Any) -> None:
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(*args)
            else:
                callback(*args)
        except Exception as e:
            logger.error(f"Error in event callback: {e}")

    # Utility methods
    async def wait_for_connection(self, timeout: Optional[float] = None) -> None:
        if not self.socket:
            raise Exception("WebSocket not initialized")
        
        try:
            await asyncio.wait_for(self.socket.wait_for_connection(), timeout=timeout)
        except asyncio.TimeoutError:
            raise Exception("Connection timeout")

    def set_subprotocol(self, subprotocol: str) -> None:
        if self.socket:
            self.socket.subprotocol = subprotocol

    def get_subprotocol(self) -> Optional[str]:
        return self.socket.subprotocol if self.socket else None

    def set_compression(self, compress: Optional[int] = None) -> None:
        if self.socket:
            self.socket.compression = compress

    def get_compression(self) -> Optional[int]:
        return self.socket.compression if self.socket else None

@property
def socket_info(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "is_open": self.is_open,
            "is_closed": self.is_closed,
            "is_closing": self.is_closing,
            "is_connecting": self.is_connecting,
            "subprotocol": self.get_subprotocol(),
            "compression": self.get_compression(),
        }

    # New method to handle unexpected responses
async def _handle_unexpected_response(self, status_code: int, headers: Dict[str, str]) -> None:
        logger.warning(f"Received unexpected response: status_code={status_code}")
        self.emit('unexpected-response', status_code, headers)



# # Example usage
# async def main():
#     config = SocketConfig(
#         ping_interval=30.0,
#         ping_timeout=10.0,
#         pong_timeout=10.0,
#         reconnect_interval=5.0,
#         max_reconnect_attempts=5,
#         connect_timeout_ms=5000,
#         options={"headers": {"User-Agent": "MyApp/1.0"}}
#     )
    
#     client = WebSocketClient("wss://echo.websocket.org", config)
    
#     def on_open():
#         print("WebSocket opened")
    
#     def on_message(message):
#         print(f"Received message: {message}")
    
#     def on_close(code, reason):
#         print(f"WebSocket closed: code={code}, reason={reason}")
    
#     def on_error(error):
#         print(f"WebSocket error: {error}")
    
#     client.on('open', on_open)
#     client.on('message', on_message)
#     client.on('close', on_close)
#     client.on('error', on_error)
#     client.on('upgrade', lambda headers: print(f"Connection upgraded: {headers}"))
#     client.on('unexpected-response', lambda status, headers: print(f"Unexpected response: {status}, {headers}"))
    
#     await client.connect()
#     await client.send("Hello, WebSocket!")
#     await asyncio.sleep(5)
#     await client.close()

# if __name__ == "__main__":
#     asyncio.run(main())