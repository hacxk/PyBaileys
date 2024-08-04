from typing import List, Union, Dict, TypedDict
from wabinary.constants import BinaryNodeCodingOptions
from wabinary.jid import FullJid, jid_decode

class BinaryNode(TypedDict):
    tag: str
    attrs: Dict[str, str]
    content: Union[List["BinaryNode"], str, bytes]

def encode_binary_node(node: BinaryNode, opts: BinaryNodeCodingOptions = BinaryNodeCodingOptions, buffer: bytearray = bytearray()) -> bytes:
    encoded = encode_binary_node_inner(node, opts, buffer)
    return bytes(encoded)

def encode_binary_node_inner(node: BinaryNode, opts: BinaryNodeCodingOptions, buffer: bytearray) -> bytearray:
    TAGS = opts.TAGS
    TOKEN_MAP = opts.TOKEN_MAP

    def push_byte(value: int) -> None:
        buffer.append(value & 0xff)

    def push_int(value: int, n: int, little_endian: bool = False) -> None:
        for i in range(n):
            cur_shift = i if little_endian else n - 1 - i
            buffer.append((value >> (cur_shift * 8)) & 0xff)

    def push_bytes(bytes_: Union[bytearray, bytes, List[int]]) -> None:
        buffer.extend(bytes_)

    def push_int16(value: int) -> None:
        push_bytes([(value >> 8) & 0xff, value & 0xff])

    def push_int20(value: int) -> None:
        push_bytes([(value >> 16) & 0x0f, (value >> 8) & 0xff, value & 0xff])

    def write_byte_length(length: int) -> None:
        if length >= 4294967296:
            raise ValueError('string too large to encode: ' + str(length))

        if length >= 1 << 20:
            push_byte(TAGS['BINARY_32'])
            push_int(length, 4)  # 32 bit integer
        elif length >= 256:
            push_byte(TAGS['BINARY_20'])
            push_int20(length)
        else:
            push_byte(TAGS['BINARY_8'])
            push_byte(length)

    def write_string_raw(s: str) -> None:
        bytes_ = s.encode('utf-8')
        write_byte_length(len(bytes_))
        push_bytes(bytes_)

    def write_jid(jid: FullJid) -> None:
        if jid.get('device') is not None:
            push_byte(TAGS['AD_JID'])
            push_byte(jid.get('domainType', 0))
            push_byte(jid.get('device', 0))
            write_string(jid['user'])
        else:
            push_byte(TAGS['JID_PAIR'])
            if jid['user']:
                write_string(jid['user'])
            else:
                push_byte(TAGS['LIST_EMPTY'])
            write_string(jid['server'])

    def pack_nibble(char: str) -> int:
        if char == '-':
            return 10
        elif char == '.':
            return 11
        elif char == '\0':
            return 15
        elif '0' <= char <= '9':
            return ord(char) - ord('0')
        else:
            raise ValueError(f'invalid byte for nibble "{char}"')

    def pack_hex(char: str) -> int:
        if '0' <= char <= '9':
            return ord(char) - ord('0')
        elif 'A' <= char <= 'F':
            return 10 + ord(char) - ord('A')
        elif 'a' <= char <= 'f':
            return 10 + ord(char) - ord('a')
        elif char == '\0':
            return 15
        else:
            raise ValueError(f'Invalid hex char "{char}"')

    def write_packed_bytes(s: str, type_: str) -> None:
        if len(s) > TAGS['PACKED_MAX']:
            raise ValueError('Too many bytes to pack')

        push_byte(TAGS['NIBBLE_8'] if type_ == 'nibble' else TAGS['HEX_8'])

        rounded_length = -(-len(s) // 2)
        if len(s) % 2 != 0:
            rounded_length |= 128

        push_byte(rounded_length)
        pack_function = pack_nibble if type_ == 'nibble' else pack_hex

        def pack_byte_pair(v1: str, v2: str) -> int:
            return (pack_function(v1) << 4) | pack_function(v2)

        for i in range(len(s) // 2):
            push_byte(pack_byte_pair(s[2 * i], s[2 * i + 1]))

        if len(s) % 2 != 0:
            push_byte(pack_byte_pair(s[-1], '\x00'))

    def is_nibble(s: str) -> bool:
        if len(s) > TAGS['PACKED_MAX']:
            return False
        return all(char in '0123456789-.' for char in s)

    def is_hex(s: str) -> bool:
        if len(s) > TAGS['PACKED_MAX']:
            return False
        return all(char in '0123456789ABCDEFabcdef' or char == '\0' for char in s)

    def write_string(s: str) -> None:
        token_index = TOKEN_MAP.get(s)
        if token_index:
            if 'dict' in token_index:
                push_byte(TAGS['DICTIONARY_0'] + token_index['dict'])
            push_byte(token_index['index'])
        elif is_nibble(s):
            write_packed_bytes(s, 'nibble')
        elif is_hex(s):
            write_packed_bytes(s, 'hex')
        else:
            decoded_jid = jid_decode(s)
            if decoded_jid:
                write_jid(decoded_jid)
            else:
                write_string_raw(s)

    def write_list_start(list_size: int) -> None:
        if list_size == 0:
            push_byte(TAGS['LIST_EMPTY'])
        elif list_size < 256:
            push_bytes([TAGS['LIST_8'], list_size])
        else:
            push_byte(TAGS['LIST_16'])
            push_int16(list_size)

    valid_attributes = {k: v for k, v in node['attrs'].items() if v is not None}

    write_list_start(2 * len(valid_attributes) + 1 + (1 if node.get('content') is not None else 0))
    write_string(node['tag'])

    for key, value in valid_attributes.items():
        write_string(key)
        write_string(value)

    content = node.get('content')
    if isinstance(content, str):
        write_string(content)
    elif isinstance(content, (bytes, bytearray)):
        write_byte_length(len(content))
        push_bytes(content)
    elif isinstance(content, list):
        write_list_start(len(content))
        for item in content:
            encode_binary_node_inner(item, opts, buffer)
    elif content is None:
        pass
    else:
        raise ValueError(f'invalid children for header "{node["tag"]}": {content} ({type(content)})')

    return buffer
