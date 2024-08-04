from typing import TypedDict, Literal
from datetime import datetime 

WACallUpdateType = Literal['offer', 'ringing', 'timeout', 'reject', 'accept']


class WACallEvent(TypedDict):
    chatId: str
    jid: str
    isGroup: bool
    groupJid: str
    id: str
    date: datetime
    isVideo: bool
    status: WACallUpdateType
    offline: bool
    latencyMs: int
