import os
import random
import hashlib
import time
import json
import base64
import struct
import asyncio
import threading
import math
from typing import Dict, List, Tuple, Union, Optional
from datetime import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import aiohttp  # Changed from axions to aiohttp for async HTTP requests
from proto.waproto_pb2 import DeviceProps, IMessageKey, Message, WebMessageInfo
from types.events_types import BaileysEventEmitter, BaileysEventMap
from models.closeing_models import DisconnectReason
from types.call_types import WACallUpdateType
from defaults.defaults import WAVersion
from types.browser_types import BrowsersMap
from wabinary.jid import jid_decode
from wabinary.generic import get_all_binary_node_children
from models.other_models import BinaryNode

# Read the JSON file containing phone number to MCC (Mobile Country Code) mappings
with open("src/defaults/baileys-version.json", 'r') as file:
    version = json.load(file)

PLATFORM_MAP = {
    'aix': 'AIX',
    'darwin': 'Mac OS',
    'win32': 'Windows',
    'android': 'Android',
    'freebsd': 'FreeBSD',
    'openbsd': 'OpenBSD',
    'sunos': 'Solaris'
}

Browsers: BrowsersMap = {
    'ubuntu': lambda browser: ['Ubuntu', browser, '22.04.4'],
    'macOS': lambda browser: ['Mac OS', browser, '14.4.1'],
    'baileys': lambda browser: ['Baileys', browser, '6.5.0'],
    'windows': lambda browser: ['Windows', browser, '10.0.22631'],
    'appropriate': lambda browser: [PLATFORM_MAP.get(os.name, 'Ubuntu'), browser, os.release()]
}

def get_platform_id(browser: str) -> str:
    platform_type = DeviceProps.PlatformType.Value(browser.upper())
    return str(ord(chr(platform_type))) if platform_type else '49'  # chrome

class BufferJSON:
    @staticmethod
    def replacer(k, value):
        if isinstance(value, bytes) or isinstance(value, bytearray) or getattr(value, 'type', None) == 'Buffer':
            return {'type': 'Buffer', 'data': base64.b64encode(value).decode()}
        return value

    @staticmethod
    def reviver(_, value):
        if isinstance(value, dict) and (value.get('buffer') == True or value.get('type') == 'Buffer'):
            val = value.get('data') or value.get('value')
            return base64.b64decode(val) if isinstance(val, str) else bytes(val or [])
        return value

def get_key_author(key: Optional[IMessageKey], me_id: str = 'me') -> str:
    return (me_id if key and key.from_me else (key.participant or key.remote_jid)) if key else ''

def write_random_pad_max16(msg: bytes) -> bytes:
    pad = os.urandom(1)
    pad_val = pad[0] & 0xf
    if not pad_val:
        pad_val = 0xf
    return msg + bytes([pad_val] * pad_val)

def unpad_random_max16(e: bytes) -> bytes:
    if not e:
        raise ValueError('unpadPkcs7 given empty bytes')
    r = e[-1]
    if r > len(e):
        raise ValueError(f'unpad given {len(e)} bytes, but pad is {r}')
    return e[:-r]

def encode_wa_message(message: Message) -> bytes:
    return write_random_pad_max16(message.SerializeToString())

def generate_registration_id() -> int:
    return int.from_bytes(os.urandom(2), 'big') & 16383

def encode_big_endian(e: int, t: int = 4) -> bytes:
    return e.to_bytes(t, 'big')

def to_number(t: Union[int, int]) -> int:  # Changed 'Long' to int
    return t.low if hasattr(t, 'low') else int(t)

def unix_timestamp_seconds(date: datetime = None) -> int:
    return int((date or datetime.now()).timestamp())

class DebouncedTimeout:
    def __init__(self, interval_ms: int = 1000, task=None):
        self.interval_ms = interval_ms
        self.task = task
        self.timeout = None

    def start(self, new_interval_ms=None, new_task=None):
        self.task = new_task or self.task
        self.interval_ms = new_interval_ms or self.interval_ms
        if self.timeout:
            self.timeout.cancel()
        self.timeout = threading.Timer(self.interval_ms / 1000, self.task)
        self.timeout.start()

    def cancel(self):
        if self.timeout:
            self.timeout.cancel()
            self.timeout = None

    def set_task(self, new_task):
        self.task = new_task

    def set_interval(self, new_interval):
        self.interval_ms = new_interval

def delay(ms: int):
    return time.sleep(ms / 1000)

class DelayCancellable:
    def __init__(self, ms: int):
        self.ms = ms
        self.timer = None
        self.future = None

    async def delay(self):
        self.future = asyncio.Future()
        self.timer = asyncio.get_event_loop().call_later(self.ms / 1000, self.future.set_result, None)
        try:
            await self.future
        except asyncio.CancelledError:
            self.timer.cancel()
            raise

    def cancel(self):
        if self.future and not self.future.done():
            self.future.cancel()

async def promise_timeout(ms: Optional[int], promise):
    if not ms:
        return await promise
    try:
        return await asyncio.wait_for(promise, timeout=ms/1000)
    except asyncio.TimeoutError:
        raise Exception('Timed Out')

def generate_message_id_v2(user_id: Optional[str] = None) -> str:
    data = bytearray(44)
    struct.pack_into('>Q', data, 0, int(time.time()))
    if user_id:
        id_parts = jid_decode(user_id)
        if id_parts and id_parts.user:
            data[8:8+len(id_parts.user)] = id_parts.user.encode()
            data[8+len(id_parts.user):8+len(id_parts.user)+5] = b'@c.us'
    data[28:] = os.urandom(16)
    return '3EB0' + hashlib.sha256(data).hexdigest().upper()[:18]

def generate_message_id() -> str:
    return '3EB0' + os.urandom(18).hex().upper()

def bind_wait_for_event(ev: BaileysEventEmitter, event: str):
    async def wait_for(check, timeout_ms=None):
        future = asyncio.Future()
        
        def listener(update):
            if check(update):
                future.set_result(None)
        
        def close_listener(connection, last_disconnect):
            if connection == 'close':
                future.set_exception(last_disconnect.error if last_disconnect else Exception('Connection Closed'))
        
        ev.on(event, listener)
        ev.on('connection.update', close_listener)
        
        try:
            await asyncio.wait_for(future, timeout=timeout_ms/1000 if timeout_ms else None)
        finally:
            ev.off(event, listener)
            ev.off('connection.update', close_listener)
    
    return wait_for

bind_wait_for_connection_update = lambda ev: bind_wait_for_event(ev, 'connection.update')

def print_qr_if_necessary_listener(ev: BaileysEventEmitter, logger):
    def on_connection_update(update):
        if update.get('qr'):
            try:
                import qrcode
                qr = qrcode.QRCode()
                qr.add_data(update['qr'])
                qr.print_tty()
            except ImportError:
                logger.error('QR code terminal not added as dependency')
    
    ev.on('connection.update', on_connection_update)

async def fetch_latest_baileys_version(options=None):
    URL = 'https://raw.githubusercontent.com/WhiskeySockets/Baileys/master/src/Defaults/baileys-version.json'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(URL, **options) as response:
                data = await response.json()
                return {
                    'version': data['version'],
                    'isLatest': True
                }
    except Exception as error:
        return {
            'version': version['version'],
            'isLatest': False,
            'error': str(error)
        }

async def fetch_latest_wa_web_version(options):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://web.whatsapp.com/check-update?version=1&platform=web', **options) as response:
                data = await response.json()
                version = data['currentVersion'].split('.')
                return {
                    'version': [int(v) for v in version[:3]],
                    'isLatest': True
                }
    except Exception as error:
        return {
            'version': version['version'],
            'isLatest': False,
            'error': str(error)
        }

def generate_md_tag_prefix() -> str:
    bytes_val = os.urandom(4)
    return f"{int.from_bytes(bytes_val[:2], 'big')}.{int.from_bytes(bytes_val[2:], 'big')}-"

STATUS_MAP = {
    'played': WebMessageInfo.Status.PLAYED,
    'read': WebMessageInfo.Status.READ,
    'read-self': WebMessageInfo.Status.READ
}

def get_status_from_receipt_type(type_: Optional[str]) -> WebMessageInfo.Status:
    if type_ is None:
        return WebMessageInfo.Status.DELIVERY_ACK
    return STATUS_MAP.get(type_, WebMessageInfo.Status.DELIVERY_ACK)

CODE_MAP = {
    'conflict': DisconnectReason.CONNECTION_REPLACED
}

def get_error_code_from_stream_error(node: BinaryNode) -> Dict[str, Union[str, int]]:
    reason_node = get_all_binary_node_children(node)[0] if get_all_binary_node_children(node) else None
    reason = reason_node.tag if reason_node else 'unknown'
    status_code = int(node.attrs.get('code', CODE_MAP.get(reason, DisconnectReason.BAD_SESSION)))
    
    if status_code == DisconnectReason.RESTART_REQUIRED:
        reason = 'restart required'
    
    return {
        'reason': reason,
        'statusCode': status_code
    }

def get_call_status_from_node(node: BinaryNode) -> WACallUpdateType:
    tag, attrs = node.tag, node.attrs
    if tag in ['offer', 'offer_notice']:
        return 'offer'
    elif tag == 'terminate':
        return 'timeout' if attrs.get('reason') == 'timeout' else 'reject'
    elif tag == 'reject':
        return 'reject'
    elif tag == 'accept':
        return 'accept'
    else:
        return 'ringing'

UNEXPECTED_SERVER_CODE_TEXT = 'Unexpected server response: '

def get_code_from_ws_error(error: Exception) -> int:
    status_code = 500
    if isinstance(error, str) and UNEXPECTED_SERVER_CODE_TEXT in error:
        code = int(error.split(UNEXPECTED_SERVER_CODE_TEXT)[-1])
        if not math.isnan(code) and code >= 400:
            status_code = code
    elif getattr(error, 'code', '').startswith('E') or 'timed out' in str(error):
        status_code = 408
    return status_code

def is_wa_business_platform(platform: str) -> bool:
    return platform in ['smbi', 'smba']

def trim_undefined(obj: dict) -> dict:
    return {k: v for k, v in obj.items() if v is not None}

CROCKFORD_CHARACTERS = '123456789ABCDEFGHJKLMNPQRSTVWXYZ'

def bytes_to_crockford(buffer: bytes) -> str:
    value = int.from_bytes(buffer, 'big')
    crockford = []
    while value > 0:
        crockford.append(CROCKFORD_CHARACTERS[value & 31])
        value >>= 5
    return ''.join(reversed(crockford))