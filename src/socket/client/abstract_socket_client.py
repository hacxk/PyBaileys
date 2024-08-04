import asyncio
from abc import ABC, abstractmethod
from typing import Callable, Optional, Union
from urllib.parse import urlparse
from defaults.defaults import SocketConfig

class AbstractSocketClient(ABC):
    def __init__(self, url: str, config: SocketConfig) -> None:
        self.url = urlparse(url)  # Use urlparse to handle URL
        self.config = config
        self._event_listeners = {}  # Dictionary to manage event listeners

        # Set maximum listeners if needed
        self.max_listeners = 10  # Example value, adjust as needed

    @property
    @abstractmethod
    def is_open(self) -> bool:
        """Property to check if the socket is open."""
        pass

    @property
    @abstractmethod
    def is_closed(self) -> bool:
        """Property to check if the socket is closed."""
        pass

    @property
    @abstractmethod
    def is_closing(self) -> bool:
        """Property to check if the socket is closing."""
        pass

    @property
    @abstractmethod
    def is_connecting(self) -> bool:
        """Property to check if the socket is connecting."""
        pass

    @abstractmethod
    async def connect(self) -> None:
        """Asynchronous method to connect the socket."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Asynchronous method to close the socket."""
        pass

    @abstractmethod
    async def send(self, data: Union[bytes, str], callback: Optional[Callable[[Optional[Exception]], None]] = None) -> bool:
        """
        Asynchronous method to send data through the socket.

        Args:
            data (Union[bytes, str]): The data to send, can be bytes or string.
            callback (Optional[Callable[[Optional[Exception]], None]]): Optional callback to handle errors.

        Returns:
            bool: Whether the send operation was successful.
        """
        pass

    def on(self, event: str, listener: Callable[..., None]) -> None:
        """Add an event listener with a check for the maximum number of listeners."""
        if event not in self._event_listeners:
            self._event_listeners[event] = []
        if len(self._event_listeners[event]) < self.max_listeners:
            self._event_listeners[event].append(listener)
        else:
            raise RuntimeError("Maximum number of event listeners reached")

    def emit(self, event: str, *args, **kwargs) -> None:
        """Emit an event to all registered listeners."""
        if event in self._event_listeners:
            for listener in self._event_listeners[event]:
                listener(*args, **kwargs)

    def remove_listener(self, event: str, listener: Callable[..., None]) -> None:
        """Remove an event listener."""
        if event in self._event_listeners:
            self._event_listeners[event].remove(listener)
