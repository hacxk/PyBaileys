import asyncio
from typing import Callable, Optional, Union
from defaults.defaults import SocketConfig
from .abstract_socket_client import AbstractSocketClient  # Import the AbstractSocketClient

class ConcreteSocketClient(AbstractSocketClient):
    def __init__(self, url: str, config: SocketConfig) -> None:
        super().__init__(url, config)
        # Initialize other attributes if needed
        self._is_open = False
        self._is_closed = True
        self._is_closing = False
        self._is_connecting = False

    @property
    def is_open(self) -> bool:
        return self._is_open

    @property
    def is_closed(self) -> bool:
        return self._is_closed

    @property
    def is_closing(self) -> bool:
        return self._is_closing

    @property
    def is_connecting(self) -> bool:
        return self._is_connecting

    async def connect(self) -> None:
        # Simulate connecting
        self._is_connecting = True
        await asyncio.sleep(1)  # Simulate async operation
        self._is_connecting = False
        self._is_open = True
        self._is_closed = False
        print("Connected")

    async def close(self) -> None:
        # Simulate closing
        self._is_closing = True
        await asyncio.sleep(1)  # Simulate async operation
        self._is_closing = False
        self._is_open = False
        self._is_closed = True
        print("Closed")

    async def send(self, data: Union[bytes, str], callback: Optional[Callable[[Optional[Exception]], None]] = None) -> bool:
        # Simulate sending data
        try:
            await asyncio.sleep(1)  # Simulate async operation
            print(f"Sent: {data}")
            if callback:
                callback(None)  # No error
            return True
        except Exception as e:
            if callback:
                callback(e)  # Pass the error to the callback
            return False
