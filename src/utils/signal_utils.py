from defaults.defaults import KEY_BUNDLE_TYPE
from types.signal_types import SignalRepository
from models.sock_models import AuthenticationCreds, AuthenticationState, KeyPair, SignalIdentity, SignalKeyStore, SignedKeyPair
from models.other_models import BinaryNode
from wabinary.generic import (
    assert_node_error_free, 
    get_binary_node_child, 
    get_binary_node_child_buffer, 
    get_binary_node_children, 
    get_binary_node_child_uint
)
from wabinary.jid import (
    S_WHATSAPP_NET, 
    jid_decode, 
    JidWithDevice
)
from utils.crypto_utils import Curve, generate_signal_pub_key
from .generics_utils import encode_big_endian
from typing import Dict, List, Optional, Tuple, Union

def create_signal_identity(wid: str, account_signature_key: bytes) -> SignalIdentity:
    return SignalIdentity(
        identifier={
            'name': wid, 
            'deviceId': 0
        },
        identifier_key=generate_signal_pub_key(account_signature_key)
    )

async def get_pre_keys(key_store: SignalKeyStore, min_id: int, limit: int) -> Dict[str, bytes]:
    id_list = [str(id) for id in range(min_id, limit)]
    return await key_store.get('pre-key', id_list)

def generate_or_get_pre_keys(creds: AuthenticationCreds, range: int) -> Dict[str, Union[Dict[int, KeyPair], int, Tuple[int, int]]]:
    available = creds.nextPreKeyId - creds.firstUnuploadedPreKeyId
    remaining = range - available
    last_pre_key_id = creds.nextPreKeyId + remaining - 1
    new_pre_keys: Dict[int, KeyPair] = {}
    if remaining > 0:
        for i in range(creds.nextPreKeyId, last_pre_key_id + 1):
            new_pre_keys[i] = Curve.generate_key_pair()

    return {
        'newPreKeys': new_pre_keys,
        'lastPreKeyId': last_pre_key_id,
        'preKeysRange': (creds.firstUnuploadedPreKeyId, range)
    }

def xmpp_signed_pre_key(key: SignedKeyPair) -> BinaryNode:
    return BinaryNode(
        tag='skey',
        attrs={},
        content=[
            BinaryNode(tag='id', attrs={}, content=encode_big_endian(key.keyId, 3)),
            BinaryNode(tag='value', attrs={}, content=key.keyPair.public),
            BinaryNode(tag='signature', attrs={}, content=key.signature)
        ]
    )

def xmpp_pre_key(pair: KeyPair, id: int) -> BinaryNode:
    return BinaryNode(
        tag='key',
        attrs={},
        content=[
            BinaryNode(tag='id', attrs={}, content=encode_big_endian(id, 3)),
            BinaryNode(tag='value', attrs={}, content=pair.public)
        ]
    )

async def parse_and_inject_e2e_sessions(node: BinaryNode, repository: SignalRepository) -> None:
    def extract_key(key: Optional[BinaryNode]) -> Optional[Dict[str, Union[int, bytes]]]:
        if not key:
            return None
        return {
            'keyId': get_binary_node_child_uint(key, 'id', 3),
            'publicKey': generate_signal_pub_key(get_binary_node_child_buffer(key, 'value')),
            'signature': get_binary_node_child_buffer(key, 'signature')
        }

    nodes = get_binary_node_children(get_binary_node_child(node, 'list'), 'user')
    for node in nodes:
        assert_node_error_free(node)

    chunk_size = 100
    chunks = [nodes[i:i + chunk_size] for i in range(0, len(nodes), chunk_size)]
    for nodes_chunk in chunks:
        for node in nodes_chunk:
            signed_key = get_binary_node_child(node, 'skey')
            key = get_binary_node_child(node, 'key')
            identity = get_binary_node_child_buffer(node, 'identity')
            jid = node.attrs['jid']
            registration_id = get_binary_node_child_uint(node, 'registration', 4)

            await repository.inject_e2e_session({
                'jid': jid,
                'session': {
                    'registrationId': registration_id,
                    'identityKey': generate_signal_pub_key(identity),
                    'signedPreKey': extract_key(signed_key),
                    'preKey': extract_key(key)
                }
            })

def extract_device_jids(result: BinaryNode, my_jid: str, exclude_zero_devices: bool) -> List[JidWithDevice]:
    my_user, my_device = jid_decode(my_jid)
    extracted: List[JidWithDevice] = []
    for node in result.content:
        list_node = get_binary_node_child(node, 'list')
        if list_node and isinstance(list_node.content, list):
            for item in list_node.content:
                user = jid_decode(item.attrs['jid'])[0]
                devices_node = get_binary_node_child(item, 'devices')
                device_list_node = get_binary_node_child(devices_node, 'device-list')
                if isinstance(device_list_node.content, list):
                    for device_node in device_list_node.content:
                        device = int(device_node.attrs['id'])
                        if (
                            device_node.tag == 'device' and
                            (not exclude_zero_devices or device != 0) and
                            (my_user != user or my_device != device) and
                            (device == 0 or 'key-index' in device_node.attrs)
                        ):
                            extracted.append({'user': user, 'device': device})
    return extracted

async def get_next_pre_keys(auth_state: AuthenticationState, count: int) -> Dict[str, Union[Dict[str, Union[int, str]], Dict[str, KeyPair]]]:
    creds = auth_state.creds
    result = generate_or_get_pre_keys(creds, count)
    update = {
        'nextPreKeyId': max(result['lastPreKeyId'] + 1, creds.nextPreKeyId),
        'firstUnuploadedPreKeyId': max(creds.firstUnuploadedPreKeyId, result['lastPreKeyId'] + 1)
    }
    await auth_state.keys.set({'pre-key': result['newPreKeys']})
    pre_keys = await get_pre_keys(auth_state.keys, result['preKeysRange'][0], result['preKeysRange'][0] + result['preKeysRange'][1])
    return {'update': update, 'preKeys': pre_keys}

async def get_next_pre_keys_node(state: AuthenticationState, count: int) -> Dict[str, Union[Dict[str, Union[int, str]], BinaryNode]]:
    creds = state.creds
    result = await get_next_pre_keys(state, count)
    node = BinaryNode(
        tag='iq',
        attrs={
            'xmlns': 'encrypt',
            'type': 'set',
            'to': S_WHATSAPP_NET
        },
        content=[
            BinaryNode(tag='registration', attrs={}, content=encode_big_endian(creds.registrationId)),
            BinaryNode(tag='type', attrs={}, content=KEY_BUNDLE_TYPE),
            BinaryNode(tag='identity', attrs={}, content=creds.signedIdentityKey.public),
            BinaryNode(tag='list', attrs={}, content=[xmpp_pre_key(pair, int(k)) for k, pair in result['preKeys'].items()]),
            xmpp_signed_pre_key(creds.signedPreKey)
        ]
    )
    return {'update': result['update'], 'node': node}