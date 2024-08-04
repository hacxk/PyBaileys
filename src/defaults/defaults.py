import json
import hashlib
import binascii
import re
from typing import Tuple, Callable, List, Optional, Dict, Any
import logging
from dataclasses import dataclass

# Import the Message class from the generated protobuf module
from proto.waproto_pb2 import Message
from models.sock_models import AuthenticationState
from models.message_models import MediaType

# Define a list of HTTP status codes indicating unauthorized access
UNAUTHORIZED_CODES = [401, 403, 419]

# Read the JSON file containing phone number to MCC (Mobile Country Code) mappings
with open("src/defaults/phonenumber-mcc.json", 'r') as file:
    phoneNumberMCC = json.load(file)

# Assign the parsed phone number MCC data to a constant
PHONENUMBER_MCC = phoneNumberMCC

# Define constants for various endpoints and prefixes used in the application
DEFAULT_ORIGIN = 'https://web.whatsapp.com'  # Default URL origin for WhatsApp
MOBILE_ENDPOINT = 'g.whatsapp.net'  # Mobile endpoint for WhatsApp connections
MOBILE_PORT = 443  # Default port for HTTPS connections
DEF_CALLBACK_PREFIX = 'CB:'  # Prefix used for callback identifiers
DEF_TAG_PREFIX = 'TAG:'  # Prefix used for tag identifiers
PHONE_CONNECTION_CB = 'CB:Pong'  # Callback identifier for phone connection responses

# Define the default duration for ephemeral (temporary) data in seconds (7 days)
WA_DEFAULT_EPHEMERAL = 7 * 24 * 60 * 60

# Define the WhatsApp version being used
WA_VERSION = '2.24.6.77'

# Compute the MD5 hash of the WhatsApp version and convert to hexadecimal string
WA_VERSION_HASH = hashlib.md5(WA_VERSION.encode()).hexdigest()

# Create a mobile token by concatenating the given string with the WA_VERSION_HASH and encoding it in bytes
MOBILE_TOKEN = binascii.unhexlify('0a1mLfGUIBVrMKF1RdvLI5lkRBvof6vn0fD2QRSM' + WA_VERSION_HASH)

# Define the mobile registration endpoint URL
MOBILE_REGISTRATION_ENDPOINT = 'https://v.whatsapp.net/v2'

# Define the mobile user agent string
MOBILE_USERAGENT = f'WhatsApp/{WA_VERSION} iOS/15.3.1 Device/Apple-iPhone_7'

# Define the registration public key as a bytes object
REGISTRATION_PUBLIC_KEY = bytes([
    5, 142, 140, 15, 116, 195, 235, 197, 215, 166, 134, 92, 108, 60, 132, 56, 
    86, 176, 97, 33, 204, 232, 234, 119, 77, 34, 251, 111, 18, 37, 18, 48, 45
])

# Define the noise mode string
NOISE_MODE = 'Noise_XX_25519_AESGCM_SHA256\0\0\0\0'

# Define the dictionary version
DICT_VERSION = 2

# Define the key bundle type as a bytes object
KEY_BUNDLE_TYPE = bytes([5])

# Define the noise WA header as a bytes object, including the DICT_VERSION
NOISE_WA_HEADER = bytes([87, 65, 6, DICT_VERSION])

# Define the protocol version as a list of integers
PROTOCOL_VERSION = [5, 2]

# Create the mobile noise header by concatenating 'WA' with the protocol version bytes
MOBILE_NOISE_HEADER = b'WA' + bytes(PROTOCOL_VERSION)

# Define a regular expression pattern for matching URLs
URL_REGEX = re.compile(
    r'(http(s)?://.)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)'
)

# Define certificate details with a default serial number
WA_CERT_DETAILS = {
    'SERIAL': 0  # Default serial number for the certificate
}

# Define a list of history sync types that can be processed
PROCESSABLE_HISTORY_TYPES = [
    Message.HistorySyncNotification.HistorySyncType.INITIAL_BOOTSTRAP,  # Initial sync
    Message.HistorySyncNotification.HistorySyncType.PUSH_NAME,           # Push name update
    Message.HistorySyncNotification.HistorySyncType.RECENT,              # Recent history
    Message.HistorySyncNotification.HistorySyncType.FULL                 # Full history
]

# Define the WAVersion type as a tuple of integers
WAVersion = Tuple[int, int, int]

# Define the SocketConfig class with various configuration options
@dataclass
class SocketConfig:
    version: WAVersion
    browser: str
    wa_websocket_url: str
    connect_timeout_ms: int
    keep_alive_interval_ms: int
    logger: logging.Logger
    print_qr_in_terminal: bool
    emit_own_events: bool
    default_query_timeout_ms: int
    custom_upload_hosts: List[str]
    retry_request_delay_ms: int
    max_msg_retry_count: int
    fire_init_queries: bool
    auth: AuthenticationState
    mark_online_on_connect: bool
    sync_full_history: bool
    patch_message_before_sending: Callable[[dict], dict]
    should_sync_history_message: Callable[[], bool]
    should_ignore_jid: Callable[[], bool]
    link_preview_image_thumbnail_width: int
    transaction_opts: Dict[str, int]
    generate_high_quality_link_preview: bool
    options: Dict[str, any]
    app_state_mac_verification: Dict[str, bool]
    get_message: Callable[[], Optional[dict]]
    make_signal_repository: Callable[[], any]

# Example logger setup
logger = logging.getLogger('baileys')

# Define the DEFAULT_CONNECTION_CONFIG with example values
DEFAULT_CONNECTION_CONFIG = SocketConfig(
    version=WAVersion,  # Example version, replace with actual version tuple
    browser='Chrome/ubuntu',
    wa_websocket_url='wss://web.whatsapp.com/ws/chat',
    connect_timeout_ms=20_000,
    keep_alive_interval_ms=30_000,
    logger=logger,
    print_qr_in_terminal=False,
    emit_own_events=True,
    default_query_timeout_ms=60_000,
    custom_upload_hosts=[],
    retry_request_delay_ms=250,
    max_msg_retry_count=5,
    fire_init_queries=True,
    auth=AuthenticationState,  # Placeholder, replace with actual instance
    mark_online_on_connect=True,
    sync_full_history=False,
    patch_message_before_sending=lambda msg: msg,  # No modification by default
    should_sync_history_message=lambda: True,  # Default to sync history
    should_ignore_jid=lambda: False,  # Default to not ignore JID
    link_preview_image_thumbnail_width=192,
    transaction_opts={'maxCommitRetries': 10, 'delayBetweenTriesMs': 3000},
    generate_high_quality_link_preview=False,
    options={},
    app_state_mac_verification={'patch': False, 'snapshot': False},
    get_message=lambda: None,  # Default to None
    make_signal_repository=lambda: None  # Replace with actual function
)

# Define a dictionary to map media types to their corresponding labels
MEDIA_HKDF_KEY_MAPPING = {
    'audio': 'Audio',
    'document': 'Document',
    'gif': 'Video',
    'image': 'Image',
    'ppic': '',
    'product': 'Image',
    'ptt': 'Audio',
    'sticker': 'Image',
    'video': 'Video',
    'thumbnail-document': 'Document Thumbnail',
    'thumbnail-image': 'Image Thumbnail',
    'thumbnail-video': 'Video Thumbnail',
    'thumbnail-link': 'Link Thumbnail',
    'md-msg-hist': 'History',
    'md-app-state': 'App State',
    'product-catalog-image': '',
    'payment-bg-image': 'Payment Background',
    'ptv': 'Video'
}

# Define the MEDIA_PATH_MAP dictionary with optional values for each MediaType
MEDIA_PATH_MAP: Dict[MediaType, Optional[str]] = {
    'image': '/mms/image',
    'video': '/mms/video',
    'document': '/mms/document',
    'audio': '/mms/audio',
    'sticker': '/mms/image',
    'thumbnail-link': '/mms/image',
    'product-catalog-image': '/product/image',
    'md-app-state': '',
    'md-msg-hist': '/mms/md-app-state',  
}

DEFAULT_CACHE_TTLS = {
    'SIGNAL_STORE': 5 * 60,  # 5 minutes
    'MSG_RETRY': 60 * 60,    # 1 hour
    'CALL_OFFER': 5 * 60,    # 5 minutes
    'USER_DEVICES': 5 * 60,  # 5 minutes
}
