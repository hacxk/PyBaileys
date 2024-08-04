from typing import Optional
from dataclasses import dataclass
from datetime import datetime

# Assuming Contact is defined in models.sock_models
from models.sock_models import Contact

@dataclass
class ConnectionState:
    # Connection state which can be 'open', 'connecting', or 'close'
    connection: str

    # The error that caused the connection to close
    lastDisconnect: Optional[dict] = None

    # Whether this is a new login
    isNewLogin: Optional[bool] = None

    # The current QR code
    qr: Optional[str] = None

    # Whether the device has received all pending notifications while it was offline
    receivedPendingNotifications: Optional[bool] = None

    # Legacy connection options
    legacy: Optional[dict] = None

    # Whether the client is shown as an active, online client
    isOnline: Optional[bool] = None

    def __post_init__(self):
        if self.lastDisconnect is not None:
            # Ensure lastDisconnect has a correct structure
            if not isinstance(self.lastDisconnect, dict):
                raise TypeError("lastDisconnect must be a dictionary.")
            if 'error' not in self.lastDisconnect or 'date' not in self.lastDisconnect:
                raise ValueError("lastDisconnect must contain 'error' and 'date' keys.")
            if not isinstance(self.lastDisconnect['date'], datetime):
                raise TypeError("The 'date' field in lastDisconnect must be a datetime object.")
        
        if self.legacy is not None:
            # Ensure legacy has a correct structure
            if not isinstance(self.legacy, dict):
                raise TypeError("legacy must be a dictionary.")
            if 'phoneConnected' not in self.legacy:
                raise ValueError("legacy must contain 'phoneConnected' key.")
            if 'user' in self.legacy and not isinstance(self.legacy['user'], Contact):
                raise TypeError("The 'user' field in legacy must be a Contact object.")

# Constants to represent connection states
WAConnectionState = {'open', 'connecting', 'close'}
