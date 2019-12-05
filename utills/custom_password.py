import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


def custom_key(password):

    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(password)
    return base64.urlsafe_b64encode(digest.finalize())


def encrypt(password, token):
    f = Fernet(custom_key(password))
    return f.encrypt(bytes(token))


def decrypt(password, token):
    f = Fernet(custom_key(password))

    if type(token) == bytes:
        return f.decrypt(token)
    else:
        return f.decrypt(bytes(token, encoding='utf8'))

