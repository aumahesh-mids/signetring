from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend


# https://msftstack.wordpress.com/2016/10/15/generating-rsa-keys-with-python-3/
def new_public_private_key_pair():
    key = rsa.generate_private_key(backend=default_backend(),
                                   public_exponent=65537,
                                   key_size=2048)
    public_key = key.public_key().public_bytes(encoding=serialization.Encoding.PEM,
                                               format=serialization.PublicFormat.SubjectPublicKeyInfo)
    pem = key.private_bytes(encoding=serialization.Encoding.PEM,
                            format=serialization.PrivateFormat.TraditionalOpenSSL,
                            encryption_algorithm=serialization.NoEncryption())
    public_key_str = public_key.decode('utf-8')
    private_key_str = pem.decode('utf-8')
    return public_key_str, private_key_str


def new_symmetric_key():
    return Fernet.generate_key()