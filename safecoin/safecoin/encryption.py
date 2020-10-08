import hashlib, base64
from cryptography.fernet import Fernet
import flask_scrypt


# ─── ENCRYPTION ─────────────────────────────────────────────────────────────────
def generate_key(password=''):
    if password == '':
        return Fernet.generate_key()

    if type(password) == bytes:
        password = password.decode('utf-8')

    password = password.encode('utf-8')

    key = hashlib.md5(password).hexdigest().encode('utf-8')
    key = base64.urlsafe_b64encode(key)
    return key


def decrypt(key, theThing, password=False, type_=''):

    if type(key) == str:
        key = key.encode('utf-8')

    if type(theThing) == str:
        theThing = theThing.encode('utf-8')

    if password:
        key = generate_key(key)

    if type_ == 'str':
        return (Fernet(key).decrypt(theThing)).encode('utf-8')

    return Fernet(key).decrypt(theThing)


def encrypt(key, theThing, password=False):
    if password and theThing == ("generate"):
        key = generate_key(key)
        theThing = generate_key()
        return Fernet(key).encrypt(theThing)

    if type(key) == str:
        key = key.encode('utf-8')

    if type(theThing) == str:
        theThing = theThing.encode('utf-8')

    return Fernet(key).encrypt(theThing)

# ─── ENCRYPTION ─────────────────────────────────────────────────────────────────

