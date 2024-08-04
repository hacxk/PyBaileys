from .state_types import ConnectionState
from .message_types import MessageUpsertType, MessageUserReceiptUpdate, WAMessage, WAMessageKey, WAMessageUpdate
from .label_association_types import LabelAssociation
from .labels_types import Label
from .groupmetadata_types import GroupMetadata, ParticipantAction, RequestJoinAction, RequestJoinMethod
from models.sock_models import Contact, AuthenticationCreds
from .chat_types import Chat, ChatUpdate, PresenceData
from proto.waproto_pb2 import IUserReceipt, IReaction
from .call_types import WACallEvent
import http.client  # Using http.client for handling HTTP errors in Python
from typing import Dict, List, Set, Union, Optional, Callable


class BaileysEventMap:
    # connection state has been updated -- WS closed, opened, connecting etc.
    connection_update: Optional[ConnectionState] = None
    # credentials updated -- some metadata, keys or something
    creds_update: Optional[AuthenticationCreds] = None
    # set chats (history sync), everything is reverse chronologically sorted
    messaging_history_set: Optional[Dict[str, Union[List[Chat], List[Contact], List[WAMessage], bool]]] = None
    # upsert chats
    chats_upsert: List[Chat] = []
    # update the given chats
    chats_update: List[ChatUpdate] = []
    chats_phoneNumberShare: Optional[Dict[str, str]] = None
    # delete chats with given ID
    chats_delete: List[str] = []
    # presence of contact in a chat updated
    presence_update: Optional[Dict[str, Dict[str, PresenceData]]] = None

    contacts_upsert: List[Contact] = []
    contacts_update: List[Optional[Contact]] = []

    messages_delete: Union[Dict[str, List[WAMessageKey]], Dict[str, Union[str, bool]]] = {}
    messages_update: List[WAMessageUpdate] = []
    messages_media_update: List[Dict[str, Union[WAMessageKey, Dict[str, Union[bytes, bytes]], Exception]]] = []
    # add/update the given messages. If they were received while the connection was online,
    # the update will have type: "notify"
    messages_upsert: Optional[Dict[str, Union[List[WAMessage], MessageUpsertType]]] = None
    # message was reacted to. If reaction was removed -- then "reaction.text" will be falsey
    messages_reaction: List[Dict[str, Union[WAMessageKey, List[IReaction]]]] = []

    message_receipt_update: List[MessageUserReceiptUpdate] = []

    groups_upsert: List[GroupMetadata] = []
    groups_update: List[Optional[GroupMetadata]] = []
    # apply an action to participants in a group
    group_participants_update: Optional[Dict[str, Union[str, List[str], ParticipantAction]]] = None
    group_join_request: Optional[Dict[str, Union[str, List[str], RequestJoinAction, RequestJoinMethod]]] = None

    blocklist_set: Optional[Dict[str, List[str]]] = None
    blocklist_update: Optional[Dict[str, Union[List[str], str]]] = None

    # Receive an update on a call, including when the call was received, rejected, accepted
    call: List[WACallEvent] = []
    labels_edit: Optional[Label] = None
    labels_association: Optional[Dict[str, Union[LabelAssociation, str]]] = None


class BufferedEventData:
    def __init__(self):
        self.historySets = {
            'chats': {},
            'contacts': {},
            'messages': {},
            'empty': False,
            'isLatest': False
        }
        self.chatUpserts = {}
        self.chatUpdates = {}
        self.chatDeletes = set()
        self.contactUpserts = {}
        self.contactUpdates = {}
        self.messageUpserts = {}
        self.messageUpdates = {}
        self.messageDeletes = {}
        self.messageReactions = {}
        self.messageReceipts = {}
        self.groupUpdates = {}


BaileysEvent = str


class BaileysEventEmitter:
    def __init__(self):
        self.listeners = {}

    def on(self, event: BaileysEvent, listener: Callable):
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(listener)

    def off(self, event: BaileysEvent, listener: Callable):
        if event in self.listeners:
            self.listeners[event].remove(listener)

    def removeAllListeners(self, event: BaileysEvent):
        if event in self.listeners:
            self.listeners[event] = []

    def emit(self, event: BaileysEvent, arg: Union[dict, list, str, bool, None]) -> bool:
        if event in self.listeners:
            for listener in self.listeners[event]:
                listener(arg)
            return True
        return False
