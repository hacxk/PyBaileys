# from typing import Literal, TypedDict, Optional, Union

# S_WHATSAPP_NET = "@s.whatsapp.net"
# OFFICIAL_BIZ_JID = "16505361212@c.us"
# SERVER_JID = "server@c.us"
# PSA_WID = "0@c.us"
# STORIES_JID = "status@broadcast"

# JidServer = Literal["c.us", "g.us", "broadcast", "s.whatsapp.net", "call", "lid"]


# class JidWithDevice(TypedDict):
#     user: str
#     device: Optional[int]


# class FullJid(JidWithDevice):
#     server: Union[JidServer, str]
#     domainType: Optional[int]
    
    
# def jid_encode(user: Optional[str | int], server: JidServer, device: Optional[int] = None, agent: Optional[int] = None) -> str:
#     """
#     Encodes a user ID, server, and optional device/agent information into a WhatsApp JID (Jabber ID).

#     Args:
#         user: The user ID (phone number or other identifier).
#         server: The server type (e.g., "c.us" for individual chats).
#         device: Optional device ID.
#         agent: Optional agent ID.

#     Returns:
#         The encoded JID string.
#     """

#     jid = f"{user or ''}{f'_{agent}' if agent else ''}{f':{device}' if device else ''}@{server}"
#     return jid

# def jid_decode(jid: Optional[str]) -> Optional[FullJid]:
#     """
#     Decodes a WhatsApp JID (Jabber ID) into its components.

#     Args:
#         jid: The JID string to decode.

#     Returns:
#         A FullJid object containing the decoded components, or None if the JID is invalid.
#     """

#     if not jid or not isinstance(jid, str):
#         return None

#     sep_idx = jid.find('@')
#     if sep_idx < 0:
#         return None

#     server = jid[sep_idx + 1 :]
#     user_combined = jid[:sep_idx]

#     user_agent, *device_part = user_combined.split(':')  # Use unpacking for device
#     user, *_ = user_agent.split('_')  # Use unpacking to ignore potential agent part

#     return {
#         "server": server,
#         "user": user,
#         "domainType": 1 if server == "lid" else 0,
#         "device": int(device_part[0]) if device_part else None
#     }

from proto.waproto_pb2 import Message
print(Message)