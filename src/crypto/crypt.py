import base64
import logging
from enum import Enum

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey

from crypto.key import new_symmetric_key, new_public_private_key_pair
from crypto.util import load_key, KeyType, load_key_str
from trustedauthority.app.config.settings import settings

logger = logging.getLogger(__name__)


# https://devqa.io/encrypt-decrypt-data-python/

def encrypt(plaintext: str, public_key_file) -> str:
    public_key = load_key(public_key_file, key_type=KeyType.Public)
    encrypted = base64.b64encode(public_key.encrypt(
        bytes(plaintext, 'utf-8'),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    ))
    return encrypted.hex()


def encrypt_with_key_str(plaintext: str, public_key_str) -> str:
    public_key = load_key_str(bytes(public_key_str, 'utf-8'), key_type=KeyType.Public)
    encrypted = base64.b64encode(public_key.encrypt(
        bytes(plaintext, 'utf-8'),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    ))
    return encrypted.hex()


def decrypt(ciphertext: str, private_key_file) -> str:
    private_key = load_key(private_key_file, key_type=KeyType.Private)
    encrypted = bytes.fromhex(ciphertext)
    decrypted = private_key.decrypt(
        base64.b64decode(encrypted),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted.decode('utf-8')


def decrypt_with_key_str(ciphertext, private_key_str) -> str:
    private_key = load_key_str(bytes(private_key_str, 'utf-8'), key_type=KeyType.Private)
    encrypted = bytes.fromhex(ciphertext)
    decrypted = private_key.decrypt(
        base64.b64decode(encrypted),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted.decode('utf-8')


def sym_encrypt(plaintext: str, key: bytes) -> str:
    f = Fernet(key)
    encrypted = f.encrypt(bytes(plaintext, 'utf-8'))
    return encrypted.hex()


def sym_decrypt(ciphertext: str, key: bytes) -> str:
    f = Fernet(key)
    encrypted = bytes.fromhex(ciphertext)
    decrypted = f.decrypt(encrypted)
    return decrypted.decode('utf-8')


if __name__ == '__main__':
    message = "Hello, World!"

    encrypted_message1 = encrypt(message, settings.TA_PUBLIC_KEY_FILE)
    print(encrypted_message1)
    print(decrypt(encrypted_message1, settings.TA_PRIVATE_KEY_FILE))

    symkey = new_symmetric_key()
    encrypted_message = sym_encrypt(message, symkey)
    print(encrypted_message)
    print(sym_decrypt(encrypted_message, symkey))

    x, y = new_public_private_key_pair()
    encrypted_message2 = encrypt_with_key_str(message, x)
    print(encrypted_message2)
    print(decrypt_with_key_str(encrypted_message2, y))
