from abc import ABC, abstractmethod
from typing import Dict, Union
from proto.waproto_pb2 import Message

# Define the classes as needed
class DecryptGroupSignalOpts:
    def __init__(self, group: str, author_jid: str, msg: bytes):
        self.group = group
        self.author_jid = author_jid
        self.msg = msg

class ProcessSenderKeyDistributionMessageOpts:
    def __init__(self, item: Message.SenderKeyDistributionMessage, author_jid: str):
        self.item = item
        self.author_jid = author_jid

class DecryptSignalProtoOpts:
    def __init__(self, jid: str, type: str, ciphertext: bytes):
        self.jid = jid
        self.type = type
        self.ciphertext = ciphertext

class EncryptMessageOpts:
    def __init__(self, jid: str, data: bytes):
        self.jid = jid
        self.data = data

class EncryptGroupMessageOpts:
    def __init__(self, group: str, data: bytes, me_id: str):
        self.group = group
        self.data = data
        self.me_id = me_id

class PreKey:
    def __init__(self, key_id: int, public_key: bytes):
        self.key_id = key_id
        self.public_key = public_key

class SignedPreKey(PreKey):
    def __init__(self, key_id: int, public_key: bytes, signature: bytes):
        super().__init__(key_id, public_key)
        self.signature = signature

class E2ESession:
    def __init__(self, registration_id: int, identity_key: bytes, signed_pre_key: SignedPreKey, pre_key: PreKey):
        self.registration_id = registration_id
        self.identity_key = identity_key
        self.signed_pre_key = signed_pre_key
        self.pre_key = pre_key

class E2ESessionOpts:
    def __init__(self, jid: str, session: E2ESession):
        self.jid = jid
        self.session = session

# Abstract base class for the SignalRepository
class SignalRepository(ABC):

    @abstractmethod
    async def decrypt_group_message(self, opts: DecryptGroupSignalOpts) -> bytes:
        pass

    @abstractmethod
    async def process_sender_key_distribution_message(self, opts: ProcessSenderKeyDistributionMessageOpts) -> None:
        pass

    @abstractmethod
    async def decrypt_message(self, opts: DecryptSignalProtoOpts) -> bytes:
        pass

    @abstractmethod
    async def encrypt_message(self, opts: EncryptMessageOpts) -> Dict[str, Union[str, bytes]]:
        pass

    @abstractmethod
    async def encrypt_group_message(self, opts: EncryptGroupMessageOpts) -> Dict[str, bytes]:
        pass

    @abstractmethod
    async def inject_e2e_session(self, opts: E2ESessionOpts) -> None:
        pass

    @abstractmethod
    def jid_to_signal_protocol_address(self, jid: str) -> str:
        pass
