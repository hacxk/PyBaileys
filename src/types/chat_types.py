from models.sock_models import AccountSettings
from .label_association_types import ChatLabelAssociationActionBody, MessageLabelAssociationActionBody
from .message_types import MinimalMessage
from proto.waproto_pb2 import ISyncActionData, ISyncActionValue, SyncdMutation, SyncActionValue, IConversation
from .events_types import BufferedEventData

from typing import Callable, Optional, List, Dict

# Privacy settings in WhatsApp Web
WAPrivacyValue = ['all', 'contacts', 'contact_blacklist', 'none']
WAPrivacyOnlineValue = ['all', 'match_last_seen']
WAReadReceiptsValue = ['all', 'none']
WAPrivacyCallValue = ['all', 'known']

# Set of statuses visible to other people; see updatePresence() in WhatsAppWeb.Send
WAPresence = ['unavailable', 'available', 'composing', 'recording', 'paused']

ALL_WA_PATCH_NAMES = ['critical_block', 'critical_unblock_low', 'regular_high', 'regular_low', 'regular']
WAPatchName = ALL_WA_PATCH_NAMES


class PresenceData:
    def __init__(self, last_known_presence: str, last_seen: Optional[int] = None):
        self.last_known_presence = last_known_presence
        self.last_seen = last_seen


class ChatMutation:
    def __init__(self, sync_action: ISyncActionData, index: List[str]):
        self.sync_action = sync_action
        self.index = index


class WAPatchCreate:
    def __init__(self, sync_action: ISyncActionValue, index: List[str], patch_type: str, api_version: int, operation: SyncdMutation.SyncdOperation):
        self.sync_action = sync_action
        self.index = index
        self.type = patch_type
        self.api_version = api_version
        self.operation = operation


class Chat(IConversation):
    def __init__(self, last_message_recv_timestamp: Optional[int] = None):
        super().__init__()
        self.last_message_recv_timestamp = last_message_recv_timestamp


class ChatUpdate:
    def __init__(self, chat: Optional[Chat] = None, conditional: Optional[Callable[[BufferedEventData], Optional[bool]]] = None):
        self.chat = chat
        self.conditional = conditional

    def set_conditional(self, conditional: Callable[[BufferedEventData], Optional[bool]]):
        self.conditional = conditional


class LastMessageList:
    def __init__(self, messages: Optional[List[MinimalMessage]] = None, sync_action_message_range: Optional[SyncActionValue.ISyncActionMessageRange] = None):
        self.messages = messages
        self.sync_action_message_range = sync_action_message_range


class ChatModification:
    def __init__(
        self,
        archive: Optional[bool] = None,
        last_messages: Optional[LastMessageList] = None,
        push_name_setting: Optional[str] = None,
        pin: Optional[bool] = None,
        mute: Optional[int] = None,
        clear: Optional[Dict] = None,
        star: Optional[Dict] = None,
        mark_read: Optional[bool] = None,
        delete: Optional[bool] = None,
        add_chat_label: Optional[ChatLabelAssociationActionBody] = None,
        remove_chat_label: Optional[ChatLabelAssociationActionBody] = None,
        add_message_label: Optional[MessageLabelAssociationActionBody] = None,
        remove_message_label: Optional[MessageLabelAssociationActionBody] = None
    ):
        self.archive = archive
        self.last_messages = last_messages
        self.push_name_setting = push_name_setting
        self.pin = pin
        self.mute = mute
        self.clear = clear
        self.star = star
        self.mark_read = mark_read
        self.delete = delete
        self.add_chat_label = add_chat_label
        self.remove_chat_label = remove_chat_label
        self.add_message_label = add_message_label
        self.remove_message_label = remove_message_label


class InitialReceivedChatsState:
    def __init__(self, last_msg_recv_timestamp: Optional[int] = None, last_msg_timestamp: Optional[int] = None):
        self.last_msg_recv_timestamp = last_msg_recv_timestamp
        self.last_msg_timestamp = last_msg_timestamp


class InitialAppStateSyncOptions:
    def __init__(self, account_settings: AccountSettings):
        self.account_settings = account_settings
