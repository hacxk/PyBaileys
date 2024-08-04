import random
from hashlib import md5
from typing import Dict, Optional, Union, TypedDict

from proto.waproto_pb2 import (
    ClientPayload, IClientPayload, DeviceProps, IDeviceProps,
    ADVSignedDeviceIdentityHMAC, ADVSignedDeviceIdentity, ADVDeviceIdentity, IADVSignedDeviceIdentity
)
from defaults.defaults import KEY_BUNDLE_TYPE, SocketConfig
from models.sock_models import AuthenticationCreds, SignalCreds
from wabinary.jid import S_WHATSAPP_NET, jid_decode
from models.other_models import BinaryNode
from wabinary.generic import get_binary_node_child
from .crypto_utils import Curve, hmac_sign
from .generics_utils import encode_big_endian
from .signal_utils import create_signal_identity

def get_user_agent(config: SocketConfig) -> ClientPayload.IUserAgent:
    os_version = '15.3.1' if config.mobile else '0.1'
    version = [2, 24, 6] if config.mobile else config.version
    device = 'iPhone_7' if config.mobile else 'Desktop'
    manufacturer = 'Apple' if config.mobile else ''
    platform = ClientPayload.UserAgent.Platform.IOS if config.mobile else ClientPayload.UserAgent.Platform.WEB
    phone_id = {'phoneId': config.auth.creds.phoneId} if config.mobile else {}

    return ClientPayload.IUserAgent(
        appVersion=ClientPayload.AppVersion(
            primary=version[0],
            secondary=version[1],
            tertiary=version[2]
        ),
        platform=platform,
        releaseChannel=ClientPayload.UserAgent.ReleaseChannel.RELEASE,
        mcc=config.auth.creds.registration.phoneNumberMobileCountryCode if config.auth.creds.registration else '000',
        mnc=config.auth.creds.registration.phoneNumberMobileNetworkCode if config.auth.creds.registration else '000',
        osVersion=os_version,
        manufacturer=manufacturer,
        device=device,
        osBuildNumber=os_version,
        localeLanguageIso6391='en',
        localeCountryIso31661Alpha2='US',
        **phone_id
    )

PLATFORM_MAP = {
    'Mac OS': ClientPayload.WebInfo.WebSubPlatform.DARWIN,
    'Windows': ClientPayload.WebInfo.WebSubPlatform.WIN32
}

def get_web_info(config: SocketConfig) -> ClientPayload.IWebInfo:
    web_sub_platform = ClientPayload.WebInfo.WebSubPlatform.WEB_BROWSER
    if config.syncFullHistory and PLATFORM_MAP.get(config.browser[0]):
        web_sub_platform = PLATFORM_MAP[config.browser[0]]

    return ClientPayload.IWebInfo(webSubPlatform=web_sub_platform)

def get_client_payload(config: SocketConfig) -> IClientPayload:
    payload = IClientPayload(
        connectType=ClientPayload.ConnectType.WIFI_UNKNOWN,
        connectReason=ClientPayload.ConnectReason.USER_ACTIVATED,
        userAgent=get_user_agent(config)
    )

    if not config.mobile:
        payload.webInfo = get_web_info(config)

    return payload

def generate_mobile_node(config: SocketConfig) -> IClientPayload:
    if not config.auth.creds:
        raise ValueError('No registration data found')

    payload = IClientPayload(
        **get_client_payload(config),
        sessionId=int(random.random() * 999999999 + 1),
        shortConnect=True,
        connectAttemptCount=0,
        device=0,
        dnsSource=ClientPayload.DNSSource(
            appCached=False,
            dnsMethod=ClientPayload.DNSSource.DNSResolutionMethod.SYSTEM
        ),
        passive=False,  # XMPP heartbeat setting (false: server actively pings) (true: client actively pings)
        pushName='test',
        username=int(f"{config.auth.creds.registration.phoneNumberCountryCode}{config.auth.creds.registration.phoneNumberNationalNumber}")
    )
    return IClientPayload.from_object(payload)

def generate_login_node(user_jid: str, config: SocketConfig) -> IClientPayload:
    user, device = jid_decode(user_jid)
    payload = IClientPayload(
        **get_client_payload(config),
        passive=True,
        username=int(user),
        device=device
    )
    return IClientPayload.from_object(payload)

def get_platform_type(platform: str) -> DeviceProps.PlatformType:
    platform_type = platform.upper()
    return DeviceProps.PlatformType.Value(platform_type) if platform_type in DeviceProps.PlatformType.keys() else DeviceProps.PlatformType.DESKTOP

def generate_registration_node(
    creds: SignalCreds,
    config: SocketConfig
) -> IClientPayload:
    app_version_buf = md5('.'.join(map(str, config.version)).encode()).digest()

    companion = IDeviceProps(
        os=config.browser[0],
        platformType=get_platform_type(config.browser[1]),
        requireFullSync=config.syncFullHistory
    )

    companion_proto = IDeviceProps.encode(companion).finish()

    register_payload = IClientPayload(
        **get_client_payload(config),
        passive=False,
        devicePairingData=ClientPayload.DevicePairingData(
            buildHash=app_version_buf,
            deviceProps=companion_proto,
            eRegid=encode_big_endian(creds.registrationId),
            eKeytype=KEY_BUNDLE_TYPE,
            eIdent=creds.signedIdentityKey.public,
            eSkeyId=encode_big_endian(creds.signedPreKey.keyId, 3),
            eSkeyVal=creds.signedPreKey.keyPair.public,
            eSkeySig=creds.signedPreKey.signature
        )
    )
    return IClientPayload.from_object(register_payload)

class MeInfo(TypedDict):
    id: str
    name: Optional[str]

def configure_successful_pairing(
    stanza: BinaryNode,
    creds: AuthenticationCreds
) -> Dict[str, Union[Dict[str, Union[SignalCreds, MeInfo]], BinaryNode]]:
    msg_id = stanza.attrs['id']
    pair_success_node = get_binary_node_child(stanza, 'pair-success')

    device_identity_node = get_binary_node_child(pair_success_node, 'device-identity')
    platform_node = get_binary_node_child(pair_success_node, 'platform')
    device_node = get_binary_node_child(pair_success_node, 'device')
    business_node = get_binary_node_child(pair_success_node, 'biz')

    if not device_identity_node or not device_node:
        raise ValueError('Missing device-identity or device in pair success node')

    biz_name = business_node.attrs.get('name')
    jid = device_node.attrs['jid']

    details, hmac = ADVSignedDeviceIdentityHMAC.decode(device_identity_node.content)
    adv_sign = hmac_sign(details, creds.advSecretKey.encode())
    if hmac != adv_sign:
        raise ValueError('Invalid account signature')

    account = ADVSignedDeviceIdentity.decode(details)
    account_signature_key = account.accountSignatureKey
    account_signature = account.accountSignature
    device_details = account.details
    account_msg = bytes([6, 0]) + device_details + creds.signedIdentityKey.public
    if not Curve.verify(account_signature_key, account_msg, account_signature):
        raise ValueError('Failed to verify account signature')

    device_msg = bytes([6, 1]) + device_details + creds.signedIdentityKey.public + account_signature_key
    account.deviceSignature = Curve.sign(creds.signedIdentityKey.private, device_msg)

    identity = create_signal_identity(jid, account_signature_key)
    account_enc = encode_signed_device_identity(account, False)

    device_identity = ADVDeviceIdentity.decode(account.details)

    reply = BinaryNode(
        tag='iq',
        attrs={
            'to': S_WHATSAPP_NET,
            'type': 'result',
            'id': msg_id
        },
        content=[
            BinaryNode(
                tag='pair-device-sign',
                attrs={},
                content=[
                    BinaryNode(
                        tag='device-identity',
                        attrs={'key-index': str(device_identity.keyIndex)},
                        content=[account_enc]
                    )
                ]
            )
        ]
    )

    auth_update = {
        'account': account,
        'me': {'id': jid, 'name': biz_name},
        'signalIdentities': [*creds.signalIdentities, identity],
        'platform': platform_node.attrs.get('name')
    }

    return {'creds': auth_update, 'reply': reply}

def encode_signed_device_identity(
    account: IADVSignedDeviceIdentity,
    include_signature_key: bool
) -> bytes:
    if not include_signature_key or not account.accountSignatureKey:
        account.accountSignatureKey = None

    return ADVSignedDeviceIdentity.encode(account).finish()
