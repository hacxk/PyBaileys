from models.sock_models import KeyPair
from defaults.defaults import KEY_BUNDLE_TYPE

# Import necessary modules from cryptography and other libraries
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, padding
import os
from typing import Dict, Union

# Function to generate Signal Public Key with optional prefix
def generate_signal_pub_key(pub_key: bytes) -> bytes:
    """Prefix version byte to the pub keys if necessary."""
    if len(pub_key) == 33:
        return pub_key
    else:
        return KEY_BUNDLE_TYPE + pub_key

# Curve class definition for cryptographic operations
class Curve:
    @staticmethod
    def generate_key_pair() -> KeyPair:
        """Generate a new key pair."""
        private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
        public_key = private_key.public_key()
        pub_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.CompressedPoint
        )
        return KeyPair(
            private=private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ),
            public=pub_key_bytes[1:]  # Remove version byte
        )
    
    @staticmethod
    def shared_key(private_key: bytes, public_key: bytes) -> bytes:
        """Calculate the shared key using ECDH."""
        priv_key = serialization.load_pem_private_key(private_key, password=None, backend=default_backend())
        pub_key = serialization.load_pem_public_key(public_key, backend=default_backend())
        shared = priv_key.exchange(ec.ECDH(), pub_key)
        return shared
    
    @staticmethod
    def sign(private_key: bytes, buf: bytes) -> bytes:
        """Sign a message using ECDSA."""
        priv_key = serialization.load_pem_private_key(private_key, password=None, backend=default_backend())
        signature = priv_key.sign(
            buf,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature
    
    @staticmethod
    def verify(pub_key: bytes, message: bytes, signature: bytes) -> bool:
        """Verify a message signature using ECDSA."""
        pub_key = serialization.load_pem_public_key(pub_key, backend=default_backend())
        try:
            pub_key.verify(
                signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False

# Function to create a signed key pair
def signed_key_pair(identity_key_pair: KeyPair, key_id: int) -> Dict[str, Union[KeyPair, bytes, int]]:
    """Generate a signed key pair and return it with signature and key ID."""
    pre_key = Curve.generate_key_pair()
    pub_key = generate_signal_pub_key(pre_key.public)
    signature = Curve.sign(identity_key_pair.private, pub_key)
    return {'keyPair': pre_key, 'signature': signature, 'keyId': key_id}

# AES encryption/decryption functions
def aes_encrypt_gcm(plaintext: bytes, key: bytes, iv: bytes, additional_data: bytes) -> bytes:
    """Encrypt plaintext using AES 256 GCM."""
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encryptor.authenticate_additional_data(additional_data)
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    return ciphertext + encryptor.tag

def aes_decrypt_gcm(ciphertext: bytes, key: bytes, iv: bytes, additional_data: bytes) -> bytes:
    """Decrypt ciphertext using AES 256 GCM."""
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv, ciphertext[-16:]), backend=default_backend())
    decryptor = cipher.decryptor()
    decryptor.authenticate_additional_data(additional_data)
    return decryptor.update(ciphertext[:-16]) + decryptor.finalize()

def aes_encrypt_ctr(plaintext: bytes, key: bytes, iv: bytes) -> bytes:
    """Encrypt plaintext using AES 256 CTR."""
    cipher = Cipher(algorithms.AES(key), modes.CTR(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    return encryptor.update(plaintext) + encryptor.finalize()

def aes_decrypt_ctr(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
    """Decrypt ciphertext using AES 256 CTR."""
    cipher = Cipher(algorithms.AES(key), modes.CTR(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()

def aes_decrypt(buffer: bytes, key: bytes) -> bytes:
    """Decrypt AES 256 CBC buffer with IV prefixed."""
    return aes_decrypt_with_iv(buffer[16:], key, buffer[:16])

def aes_decrypt_with_iv(buffer: bytes, key: bytes, iv: bytes) -> bytes:
    """Decrypt AES 256 CBC buffer with a given IV."""
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(buffer) + decryptor.finalize()

def aes_encrypt(buffer: bytes, key: bytes) -> bytes:
    """Encrypt buffer using AES 256 CBC with a random IV prefixed."""
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    return iv + encryptor.update(buffer) + encryptor.finalize()

def aes_encrypt_with_iv(buffer: bytes, key: bytes, iv: bytes) -> bytes:
    """Encrypt buffer using AES 256 CBC with a given IV."""
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    return encryptor.update(buffer) + encryptor.finalize()

# HMAC functions
def hmac_sign(buffer: bytes, key: bytes, variant: str = 'sha256') -> bytes:
    """Sign buffer using HMAC with specified variant (sha256 or sha512)."""
    if variant == 'sha256':
        digest = hashes.SHA256()
    elif variant == 'sha512':
        digest = hashes.SHA512()
    else:
        raise ValueError("Unsupported HMAC variant")
    h = hmac.HMAC(key, digest, backend=default_backend())
    h.update(buffer)
    return h.finalize()

def sha256(buffer: bytes) -> bytes:
    """Generate SHA-256 hash of the buffer."""
    digest = hashes.SHA256()
    h = hashes.Hash(digest, backend=default_backend())
    h.update(buffer)
    return h.finalize()

def md5(buffer: bytes) -> bytes:
    """Generate MD5 hash of the buffer."""
    digest = hashes.Hash(hashes.MD5(), backend=default_backend())
    digest.update(buffer)
    return digest.finalize()

# HKDF key expansion function
def hkdf(buffer: bytes, expanded_length: int, info: dict) -> bytes:
    """Perform HKDF key expansion."""
    salt = info.get('salt', b'')
    info_str = info.get('info', '')
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=expanded_length,
        salt=salt,
        info=info_str.encode()
    )
    return hkdf.derive(buffer)

# PBKDF2 key derivation function
async def derive_pairing_code_key(pairing_code: str, salt: bytes) -> bytes:
    """Derive key from pairing code using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=2 << 16,
        backend=default_backend()
    )
    return kdf.derive(pairing_code.encode())
