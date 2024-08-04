from enum import Enum
from typing import TypedDict, Literal, Union


class LabelAssociationType(Enum):
    CHAT = "label_jid"
    MESSAGE = "label_message"


LabelAssociationTypes = Literal["label_jid", "label_message"]


class ChatLabelAssociation(TypedDict):
    type: Literal[LabelAssociationType.CHAT]
    chatId: str
    labelId: str


class MessageLabelAssociation(TypedDict):
    type: Literal[LabelAssociationType.MESSAGE]
    chatId: str
    messageId: str
    labelId: str


LabelAssociation = Union[ChatLabelAssociation, MessageLabelAssociation]


class ChatLabelAssociationActionBody(TypedDict):
    labelId: str


class MessageLabelAssociationActionBody(TypedDict):
    labelId: str
    messageId: str
