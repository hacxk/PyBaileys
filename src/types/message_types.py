from typing import Union, List, Dict, Optional, Callable, TypedDict, Literal, Any
from datetime import datetime
from io import IOBase
from urllib.parse import urlparse

from models.sock_models import CacheStore
from .groupmetadata_types import GroupMetadata
from proto.waproto_pb2 import Message, HydratedTemplateButton, WebMessageInfo, IMessage, MessageKey, ContextInfo, UserReceipt

# Type aliases
WAMessage = WebMessageInfo
WAMessageContent = IMessage
WAContactMessage = Message.ContactMessage
WAContactsArrayMessage = Message.ContactsArrayMessage
WAMessageKey = MessageKey
WATextMessage = Message.ExtendedTextMessage
WAContextInfo = ContextInfo
WALocationMessage = Message.LocationMessage
WAGenericMediaMessage = Union[
    Message.VideoMessage,
    Message.ImageMessage,
    Message.AudioMessage,
    Message.DocumentMessage,
    Message.StickerMessage
]

# Enums
WAMessageStubType = WebMessageInfo.StubType
WAMessageStatus = WebMessageInfo.Status

# Custom types
WAMediaUpload = Union[bytes, Dict[str, str], Dict[str, IOBase]]
MessageType = Message


class DownloadableMessage(TypedDict, total=False):
    mediaKey: Optional[bytes]
    directPath: Optional[str]
    url: Optional[str]


MessageReceiptType = Literal['read', 'read-self', 'hist_sync', 'peer_msg', 'sender', 'inactive', 'played', None]


class MediaConnInfo(TypedDict):
    auth: str
    ttl: int
    hosts: List[Dict[str, Union[str, int]]]
    fetchDate: datetime


class WAUrlInfo(TypedDict, total=False):
    'canonical-url'
    'matched-text'
    title: str
    description: Optional[str]
    jpegThumbnail: Optional[bytes]
    highQualityThumbnail: Optional[Message.ImageMessage]
    originalThumbnailUrl: Optional[str]


# Types to generate WA messages
class Mentionable(TypedDict, total=False):
    mentions: List[str]


class Contextable(TypedDict, total=False):
    contextInfo: ContextInfo


class ViewOnce(TypedDict, total=False):
    viewOnce: bool


class Buttonable(TypedDict, total=False):
    buttons: List[Message.ButtonsMessage.Button]


class Templatable(TypedDict, total=False):
    templateButtons: List[HydratedTemplateButton]
    footer: Optional[str]


class Editable(TypedDict, total=False):
    edit: WAMessageKey


class Listable(TypedDict, total=False):
    sections: List[Message.ListMessage.Section]
    title: Optional[str]
    buttonText: Optional[str]


class WithDimensions(TypedDict, total=False):
    width: Optional[int]
    height: Optional[int]


class PollMessageOptions(TypedDict):
    name: str
    selectableCount: Optional[int]
    values: List[str]
    messageSecret: Optional[bytes]


class SharePhoneNumber(TypedDict):
    sharePhoneNumber: bool


class RequestPhoneNumber(TypedDict):
    requestPhoneNumber: bool


# Define possible media types explicitly
MediaType = Literal[
    'audio',
    'document',
    'gif',
    'image',
    'ppic',
    'product',
    'ptt',
    'sticker',
    'video',
    'thumbnail-document',
    'thumbnail-image',
    'thumbnail-video',
    'thumbnail-link',
    'md-msg-hist',
    'md-app-state',
    'product-catalog-image',
    'payment-bg-image',
    'ptv'
]

AnyMediaMessageContent = Any


class ButtonReplyInfo(TypedDict):
    displayText: str
    id: str
    index: int


WASendableProduct = Any  # Combination of Omit and additional fields

AnyRegularMessageContent = Any
AnyMessageContent = Any


# Updated to incorporate GroupMetadata
class GroupMetadataParticipants(TypedDict):
    participants: List[GroupMetadata.Participant]


class MinimalRelayOptions(TypedDict, total=False):
    messageId: Optional[str]
    # Updated to use GroupMetadataParticipants
    cachedGroupMetadata: Optional[Callable[[str], Optional[GroupMetadataParticipants]]]


class MessageRelayOptions(MinimalRelayOptions, total=False):
    participant: Optional[Dict[str, Union[str, int]]]
    additionalAttributes: Optional[Dict[str, str]]
    useUserDevicesCache: Optional[bool]
    statusJidList: Optional[List[str]]


class MiscMessageGenerationOptions(MinimalRelayOptions, total=False):
    timestamp: Optional[datetime]
    quoted: Optional[WAMessage]
    ephemeralExpiration: Optional[Union[int, str]]
    mediaUploadTimeoutMs: Optional[int]
    statusJidList: Optional[List[str]]
    backgroundColor: Optional[str]
    font: Optional[int]
    broadcast: Optional[bool]


class MessageGenerationOptionsFromContent(MiscMessageGenerationOptions):
    userJid: str


WAMediaUploadFunction = Callable[
    [IOBase, Dict[str, Union[str, int]]],
    Dict[str, str]
]


class MediaGenerationOptions(TypedDict, total=False):
    logger: Optional[Any]  # Logger type
    mediaTypeOverride: Optional[MediaType]
    upload: WAMediaUploadFunction
    mediaCache: Optional[CacheStore]
    mediaUploadTimeoutMs: Optional[int]
    options: Optional[Dict[str, Any]]  # AxiosRequestConfig
    backgroundColor: Optional[str]
    font: Optional[int]


class MessageContentGenerationOptions(MediaGenerationOptions, total=False):
    getUrlInfo: Optional[Callable[[str], WAUrlInfo]]


class MessageGenerationOptions(MessageContentGenerationOptions, MessageGenerationOptionsFromContent):
    pass


MessageUpsertType = Literal['append', 'notify']

MessageUserReceipt = UserReceipt


class WAMessageUpdate(TypedDict):
    update: Dict[str, Any]  # Partial<WAMessage>
    key: MessageKey


WAMessageCursor = Union[
    Dict[Literal['before'], Optional[WAMessageKey]],
    Dict[Literal['after'], Optional[WAMessageKey]]
]


class MessageUserReceiptUpdate(TypedDict):
    key: WAMessageKey
    receipt: MessageUserReceipt


class MediaDecryptionKeyInfo(TypedDict, total=False):
    iv: bytes
    cipherKey: bytes
    macKey: Optional[bytes]


class MinimalMessage(TypedDict):
    key: Any
    messageTimestamp: Any
