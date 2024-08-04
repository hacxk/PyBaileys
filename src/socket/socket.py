import asyncio
from urllib.parse import urlparse
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import logging

from defaults.defaults import SocketConfig, DEFAULT_CONNECTION_CONFIG, DEF_CALLBACK_PREFIX, DEF_TAG_PREFIX, INITIAL_PREKEY_COUNT, MIN_PREKEY_COUNT, MOBILE_ENDPOINT, MOBILE_NOISE_HEADER, MOBILE_PORT, NOISE_WA_HEADER
from models.closeing_models import DisconnectReason
from proto.waproto_pb2 import HandshakeMessage, ClientPayload, IClientPayload, IHandshakeMessage
from .client.web_socket_client import WebSocketClient
from .client.mobile_socket_client import MobileSocketClient
from wabinary.generic import assert_node_error_free, binary_node_to_string, get_binary_node_child, get_all_binary_node_children
from wabinary.jid import jid_encode, S_WHATSAPP_NET
from models.other_models import BinaryNode, encode_binary_node
from utils.auth_utils import add_transaction_capability
from utils.crypto_utils import aes_encrypt_ctr, Curve, derive_pairing_code_key
from utils.generics_utils import bind_wait_for_connection_update, bytes_to_crockford, generate_md_tag_prefix, get_code_from_ws_error, get_error_code_from_stream_error, get_platform_id, promise_timeout, print_qr_if_necessary_listener
from utils.validate_utils import configure_successful_pairing, generate_login_node, generate_mobile_node, generate_registration_node
from utils.signal_utils import get_next_pre_keys_node


class Socket:
    def __init__(self, config: SocketConfig = None):
        self.config = config or DEFAULT_CONNECTION_CONFIG
        self.logger = self.config.logger or logging.getLogger(__name__)
        self.url = self._parse_url(self.config.wa_websocket_url)
        self.ws = self._create_socket()
        self.ev = asyncio.Event()
        self.ephemeral_key_pair = ec.generate_private_key(ec.SECP256R1())
        self.creds = self.config.auth.creds if self.config.auth else None
        self.keys = add_transaction_capability(self.config.auth.keys, self.logger, self.config.transaction_opts) if self.config.auth else None
        self.closed = False
        self.uq_tag_id = generate_md_tag_prefix()
        self.epoch = 1

    def _parse_url(self, url):
        if isinstance(url, str):
            return urlparse(url)
        return url

    def _create_socket(self):
        if self.config.mobile or self.url.scheme == 'tcp':
            return MobileSocketClient(self.url, self.config)
        return WebSocketClient(self.url, self.config)

    async def connect(self):
        await self.ws.connect()
        await self.validate_connection()

    async def validate_connection(self):
        hello_msg = HandshakeMessage(
            clientHello=HandshakeMessage.ClientHello(
                ephemeral=self.ephemeral_key_pair.public_key().public_bytes(
                    encoding=serialization.Encoding.X962,
                    format=serialization.PublicFormat.UncompressedPoint
                )
            )
        )

        self.logger.info(f"Connected to WA: {self.config.browser}")

        init = hello_msg.SerializeToString()
        result = await self.await_next_message(init)
        handshake = HandshakeMessage()
        handshake.ParseFromString(result)

        self.logger.debug(f"Handshake received from WA: {handshake}")

        # Process handshake and encrypt key
        # Note: This part would need the noise protocol implementation

        if self.config.mobile:
            node = generate_mobile_node(self.config)
        elif not self.creds or not self.creds.me:
            node = generate_registration_node(self.creds, self.config)
            self.logger.info("Not logged in, attempting registration...")
        else:
            node = generate_login_node(self.creds.me.id, self.config)
            self.logger.info("Logging in...")

        payload_enc = self._encrypt_payload(node)
        await self.send_raw_message(
            HandshakeMessage(
                clientFinish=HandshakeMessage.ClientFinish(
                    static=key_enc,
                    payload=payload_enc
                )
            ).SerializeToString()
        )

        # Finish noise protocol initialization
        self.start_keep_alive_request()

    def _encrypt_payload(self, node):
        # This method would need to be implemented based on the noise protocol
        pass

    async def send_raw_message(self, data):
        if not self.ws.is_open:
            raise Exception("Connection Closed")
        
        # Encrypt frame using noise protocol
        # bytes = self.noise.encode_frame(data)
        
        await promise_timeout(
            self.config.connect_timeout_ms,
            self.ws.send(data)
        )

    def generate_message_tag(self):
        return f"{self.uq_tag_id}{self.epoch}"

    async def query(self, node, timeout_ms=None):
        if not node.attrs.get('id'):
            node.attrs['id'] = self.generate_message_tag()

        msg_id = node.attrs['id']
        wait = self.wait_for_message(msg_id, timeout_ms)

        await self.send_node(node)

        result = await wait
        if hasattr(result, 'tag'):
            assert_node_error_free(result)

        return result

    async def wait_for_message(self, msg_id, timeout_ms=None):
        future = asyncio.Future()
        
        def on_message(message):
            if not future.done():
                future.set_result(message)

        self.ws.on(f"TAG:{msg_id}", on_message)
        
        try:
            return await asyncio.wait_for(future, timeout=timeout_ms/1000 if timeout_ms else None)
        finally:
            self.ws.remove_listener(f"TAG:{msg_id}", on_message)

    async def send_node(self, frame):
        if self.logger.level == logging.DEBUG:
            self.logger.debug(f"Sending XML: {binary_node_to_string(frame)}")

        buff = encode_binary_node(frame)
        return await self.send_raw_message(buff)

    def start_keep_alive_request(self):
        asyncio.create_task(self._keep_alive_loop())

    async def _keep_alive_loop(self):
        while not self.closed:
            await asyncio.sleep(self.config.keep_alive_interval_ms / 1000)
            if self.ws.is_open:
                try:
                    await self.query({
                        'tag': 'iq',
                        'attrs': {
                            'id': self.generate_message_tag(),
                            'to': S_WHATSAPP_NET,
                            'type': 'get',
                            'xmlns': 'w:p',
                        },
                        'content': [{'tag': 'ping', 'attrs': {}}]
                    })
                except Exception as e:
                    self.logger.error(f"Error in sending keep alive: {e}")
            else:
                self.logger.warning("Keep alive called when WS not open")

    async def logout(self, msg=None):
        jid = self.creds.me.id if self.creds and self.creds.me else None
        if jid:
            await self.send_node({
                'tag': 'iq',
                'attrs': {
                    'to': S_WHATSAPP_NET,
                    'type': 'set',
                    'id': self.generate_message_tag(),
                    'xmlns': 'md'
                },
                'content': [{
                    'tag': 'remove-companion-device',
                    'attrs': {
                        'jid': jid,
                        'reason': 'user_initiated'
                    }
                }]
            })

        self.end(Exception(msg or "Intentional Logout"))

    def end(self, error=None):
        if self.closed:
            return

        self.closed = True
        self.logger.info("Connection closed" if error is None else f"Connection error: {error}")

        if not self.ws.is_closed and not self.ws.is_closing:
            self.ws.close()

        self.ev.set()

    # Add other methods like upload_pre_keys, request_pairing_code, etc.

def make_socket(config: SocketConfig = None):
    return Socket(config)