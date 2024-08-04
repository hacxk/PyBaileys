from typing import Optional, List, Dict, Union
from google.protobuf.message import Message
from proto.waproto_pb2 import WebMessageInfo  # Replace with your actual import
from models.other_models import BinaryNode  # Replace with your actual import

# some extra useful utilities

def get_binary_node_children(node: Optional[BinaryNode], child_tag: str) -> List[BinaryNode]:
    if node and isinstance(node.get('content'), list):
        return [item for item in node['content'] if item['tag'] == child_tag]
    return []

def get_all_binary_node_children(node: BinaryNode) -> List[BinaryNode]:
    if isinstance(node.get('content'), list):
        return node['content']
    return []

def get_binary_node_child(node: Optional[BinaryNode], child_tag: str) -> Optional[BinaryNode]:
    if node and isinstance(node.get('content'), list):
        return next((item for item in node['content'] if item['tag'] == child_tag), None)
    return None

def get_binary_node_child_buffer(node: Optional[BinaryNode], child_tag: str) -> Optional[Union[bytes, bytearray]]:
    child = get_binary_node_child(node, child_tag)
    if child:
        content = child.get('content')
        if isinstance(content, (bytes, bytearray)):
            return content
    return None

def get_binary_node_child_string(node: Optional[BinaryNode], child_tag: str) -> Optional[str]:
    child = get_binary_node_child(node, child_tag)
    if child:
        content = child.get('content')
        if isinstance(content, (bytes, bytearray)):
            return content.decode('utf-8')
        elif isinstance(content, str):
            return content
    return None

def get_binary_node_child_uint(node: BinaryNode, child_tag: str, length: int) -> Optional[int]:
    buff = get_binary_node_child_buffer(node, child_tag)
    if buff:
        return buffer_to_uint(buff, length)
    return None

def assert_node_error_free(node: BinaryNode):
    err_node = get_binary_node_child(node, 'error')
    if err_node:
        text = err_node.get('attrs', {}).get('text', 'Unknown error')
        code = err_node.get('attrs', {}).get('code', '0')
        raise ValueError(f"{text}: {code}")

def reduce_binary_node_to_dictionary(node: BinaryNode, tag: str) -> Dict[str, str]:
    nodes = get_binary_node_children(node, tag)
    return {
        (item['attrs'].get('name') or item['attrs'].get('config_code')): (item['attrs'].get('value') or item['attrs'].get('config_value'))
        for item in nodes
    }

def get_binary_node_messages(node: BinaryNode) -> List[Message]:
    msgs = []
    if isinstance(node.get('content'), list):
        for item in node['content']:
            if item['tag'] == 'message':
                msgs.append(WebMessageInfo.from_buffer(item['content']))
    return msgs

def buffer_to_uint(buff: Union[bytes, bytearray], length: int) -> int:
    result = 0
    for i in range(length):
        result = 256 * result + buff[i]
    return result

def binary_node_to_string(node: Optional[Union[BinaryNode, List[BinaryNode]]], indent: int = 0) -> str:
    def tabs(n: int) -> str:
        return '\t' * n

    if node is None:
        return ''

    if isinstance(node, str):
        return tabs(indent) + node

    if isinstance(node, (bytes, bytearray)):
        return tabs(indent) + node.hex()

    if isinstance(node, list):
        return '\n'.join(tabs(indent + 1) + binary_node_to_string(x, indent + 1) for x in node)

    children = binary_node_to_string(node.get('content'), indent + 1)
    tag = f"<{node['tag']} " + ' '.join(f"{k}='{v}'" for k, v in (node.get('attrs') or {}).items() if v is not None) + '>'
    content = f">\n{children}\n{tabs(indent)}</{node['tag']}>" if children else '/>'
    return tag + content
