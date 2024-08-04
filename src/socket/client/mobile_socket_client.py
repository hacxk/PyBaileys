import socket
from urllib.parse import urlparse
from typing import Optional, Callable, Union, Any
import asyncio
import logging
import select

logger = logging.getLogger(__name__)

class AbstractSocketClient:
    def __init__(self, url: str):
        self.url = urlparse(url)
        self.event_handlers = {}

    def on(self, event: str, callback: Callable):
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(callback)

    def emit(self, event: str, *args):
        if event in self.event_handlers:
            for callback in self.event_handlers[event]:
                asyncio.create_task(self._safe_callback(callback, *args))

    async def _safe_callback(self, callback: Callable, *args):
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(*args)
            else:
                callback(*args)
        except Exception as e:
            logger.error(f"Error in event callback: {e}")

class MobileSocketClient(AbstractSocketClient):
    def __init__(self, url: str):
        super().__init__(url)
        self.socket: Optional[socket.socket] = None

    @property
    def is_open(self) -> bool:
        return self.socket is not None and self.socket.fileno() != -1

    @property
    def is_closed(self) -> bool:
        return self.socket is None or self.socket.fileno() == -1

    @property
    def is_closing(self) -> bool:
        return self.is_closed

    @property
    def is_connecting(self) -> bool:
        return self.socket is not None and not self.is_open

    async def connect(self):
        if self.socket:
            return

        try:
            self.socket = socket.create_connection((self.url.hostname, int(self.url.port or 443)))
            self.socket.setblocking(False)
            
            # Emit 'connect' event
            self.emit('connect')
            
            # Emit 'ready' and 'open' events
            self.emit('ready')
            self.emit('open')

            # Start the message handler
            asyncio.create_task(self._handle_socket_events())

        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            self.emit('error', e)

    async def close(self):
        if not self.socket:
            return

        try:
            self.socket.close()
            self.emit('close')
        except Exception as e:
            logger.error(f"Error closing socket: {e}")
            self.emit('error', e)
        finally:
            self.socket = None

    def send(self, data: Union[str, bytes], cb: Optional[Callable[[Optional[Exception]], None]] = None) -> bool:
        if self.socket is None:
            return False

        try:
            if isinstance(data, str):
                data = data.encode()
            self.socket.sendall(data)
            self.emit('drain')
            if cb:
                cb(None)
            return True
        except Exception as e:
            logger.error(f"Error sending data: {e}")
            self.emit('error', e)
            if cb:
                cb(e)
            return False

    async def _handle_socket_events(self):
        while self.is_open:
            try:
                # Use select to wait for the socket to be readable
                readable, _, exceptional = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: select.select([self.socket], [], [self.socket], 0.1)
                )

                if self.socket in readable:
                    data = self.socket.recv(4096)
                    if data:
                        self.emit('data', data)
                        self.emit('message', data)
                    else:
                        # Empty data means the connection was closed
                        await self.close()
                        break

                if self.socket in exceptional:
                    # Handle exceptional condition
                    self.emit('error', Exception("Socket in exceptional condition"))
                    await self.close()
                    break

            except Exception as e:
                logger.error(f"Error in socket event handler: {e}")
                self.emit('error', e)
                await self.close()
                break

        # Emit 'end' event when the loop ends
        self.emit('end')
