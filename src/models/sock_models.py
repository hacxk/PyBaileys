from typing import Optional, List, Any, Dict, Union, TypeVar, Generic, Awaitable, Callable
from dataclasses import dataclass
from proto.waproto_pb2 import IADVSignedDeviceIdentity, Message

# Existing classes
@dataclass
class ProtocolAddress:
    name: str
    device_id: int

@dataclass
class SignalIdentity:
    identifier: ProtocolAddress
    identifier_key: bytes

@dataclass
class KeyPair:
    public: bytes
    private: bytes

@dataclass
class SignedKeyPair:
    key_pair: KeyPair
    signature: bytes
    key_id: int
    timestamp_s: Optional[int] = None

@dataclass
class SignalCreds:
    signed_identity_key: KeyPair
    signed_pre_key: KeyPair
    registration_id: int

@dataclass
class MinimalMessage:
    key: Any
    message_timestamp: int

@dataclass
class DefaultDisappearingMode:
    ephemeral_expiration: Optional[int]
    ephemeral_setting_timestamp: Optional[int]

@dataclass
class AccountSettings:
    unarchive_chats: bool
    default_disappearing_mode: Optional[DefaultDisappearingMode] = None

@dataclass
class Contact:
    id: str
    lid: Optional[str] = None
    name: Optional[str] = None
    notify: Optional[str] = None
    verified_name: Optional[str] = None
    img_url: Optional[str] = None
    status: Optional[str] = None

@dataclass
class RegistrationOptions:
    option_name: str

@dataclass
class AuthenticationCreds:
    signed_identity_key: KeyPair
    signed_pre_key: SignedKeyPair
    registration_id: int
    noise_key: KeyPair
    pairing_ephemeral_key_pair: KeyPair
    adv_secret_key: str

    me: Optional[Contact] = None
    account: Optional[IADVSignedDeviceIdentity] = None
    signal_identities: Optional[List[SignalIdentity]] = None
    my_app_state_key_id: Optional[str] = None
    first_unuploaded_pre_key_id: int
    next_pre_key_id: int

    last_account_sync_timestamp: Optional[int] = None
    platform: Optional[str] = None

    processed_history_messages: List[MinimalMessage]
    account_sync_counter: int
    account_settings: AccountSettings

    device_id: str
    phone_id: str
    identity_id: bytes
    registered: bool
    backup_token: bytes
    registration: RegistrationOptions
    pairing_code: Optional[str] = None
    last_prop_hash: Optional[str] = None
    routing_info: Optional[bytes] = None

@dataclass
class LTHashState:
    state_data: bytes

SignalDataTypeMap = Dict[
    str,
    Union[
        KeyPair,
        bytes,
        Dict[str, bool],
        Message.IAppStateSyncKeyData,
        LTHashState
    ]
]

SignalDataSet = Dict[str, Optional[Dict[str, Optional[Union[KeyPair, bytes, Dict[str, bool], Message.IAppStateSyncKeyData, LTHashState]]]]]

AwaitableType = Awaitable

class SignalKeyStore:
    async def get(self, type: str, ids: list[str]) -> Awaitable[Dict[str, SignalDataTypeMap[str]]]:
        pass

    async def set(self, data: SignalDataSet) -> Awaitable[None]:
        pass

    async def clear(self) -> Awaitable[None]:
        pass

# New AuthenticationState class
@dataclass
class AuthenticationState:
    creds: AuthenticationCreds
    keys: SignalKeyStore


T = TypeVar('T')

class CacheStore(Generic[T]):
    def get(self, key: str) -> Optional[T]:
        """
        Get a cached key and change the stats.
        """
        pass

    def set(self, key: str, value: T) -> None:
        """
        Set a key in the cache.
        """
        pass

    def del_(self, key: str) -> None:
        """
        Delete a key from the cache.
        """
        pass

    def flush_all(self) -> None:
        """
        Flush all data.
        """
        pass
    

@dataclass
class TransactionCapabilityOptions:
    max_commit_retries: int
    delay_between_tries_ms: int

class SignalKeyStoreWithTransaction(SignalKeyStore):
    async def is_in_transaction(self) -> bool:
        """
        Check if the store is currently in a transaction.
        """
        pass

    async def transaction(self, exec: Callable[[], Awaitable[T]]) -> T:
        """
        Execute a given asynchronous function within a transaction.

        :param exec: An asynchronous function to execute.
        :return: The result of the executed function.
        """
        pass