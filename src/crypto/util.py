from enum import Enum

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key


class KeyType(Enum):
    Public = "public"
    Private = "private"


def load_key(filename, key_type: KeyType):
    with open(filename, 'rb') as f:
        key = f.read()
    return load_key_str(key, key_type)


def load_key_str(key: bytes, key_type: KeyType):
    if key_type == KeyType.Public:
        key = load_pem_public_key(key, default_backend())
    elif key_type == KeyType.Private:
        key = load_pem_private_key(key, None, default_backend())
    else:
        raise Exception('unexpected key type')
    return key
