from typing import Optional, List, Dict, Union, Tuple, Callable
from defaults.defaults import SocketConfig
from models.sock_models import AuthenticationState


class UserFacingSocketConfig(SocketConfig):
    def __init__(self, auth: AuthenticationState, **kwargs):
        super().__init__(**kwargs)
        self.auth = auth


class BrowsersMap:
    def ubuntu(self, browser: str) -> Tuple[str, str, str]:
        pass

    def macOS(self, browser: str) -> Tuple[str, str, str]:
        pass

    def baileys(self, browser: str) -> Tuple[str, str, str]:
        pass

    def windows(self, browser: str) -> Tuple[str, str, str]:
        pass

    def appropriate(self, browser: str) -> Tuple[str, str, str]:
        pass


class DisconnectReason:
    connectionClosed = 428
    connectionLost = 408
    connectionReplaced = 440
    timedOut = 408
    loggedOut = 401
    badSession = 500
    restartRequired = 515
    multideviceMismatch = 411
    forbidden = 403
    unavailableService = 503


class WAInitResponse:
    def __init__(self, ref: str, ttl: int, status: int = 200):
        self.ref = ref
        self.ttl = ttl
        self.status = status


class WABusinessHoursConfig:
    def __init__(self, day_of_week: str, mode: str, open_time: Optional[int] = None, close_time: Optional[int] = None):
        self.day_of_week = day_of_week
        self.mode = mode
        self.open_time = open_time
        self.close_time = close_time


class WABusinessProfile:
    def __init__(self, description: str, email: Optional[str], business_hours: Dict[str, Optional[Union[str, List[WABusinessHoursConfig]]]], website: List[str], category: Optional[str] = None, wid: Optional[str] = None, address: Optional[str] = None):
        self.description = description
        self.email = email
        self.business_hours = business_hours
        self.website = website
        self.category = category
        self.wid = wid
        self.address = address


class CurveKeyPair:
    def __init__(self, private: bytes, public: bytes):
        self.private = private
        self.public = public
