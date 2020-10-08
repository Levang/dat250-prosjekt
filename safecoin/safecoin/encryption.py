import hashlib, base64
from cryptography.fernet import Fernet
import flask_scrypt
from safecoin.models import User

# ─── ENCRYPTION ─────────────────────────────────────────────────────────────────
def generate_key(password=''):
    if password=='':
        return Fernet.generate_key()

    if type(password)==bytes:
        password=password.decode('utf-8')

    password=password.encode('utf-8')

    key = hashlib.md5(password).hexdigest().encode('utf-8')
    key = base64.urlsafe_b64encode(key)
    return key

#Used with the activeUsers dict example
#example: decrypt(activeUsers[user.email],"Thing to decrypt")
def decrypt(key,theThing,password=False,type_=''):

    if type(key)==str:
        key=key.encode('utf-8')

    if type(theThing)==str:
        theThing=theThing.encode('utf-8')

    if password==True:
        key=generate_key(key)

    if type_=='str':
        return (Fernet(key).decrypt(theThing)).encode('utf-8')

    return (Fernet(key).decrypt(theThing))

#Used with the activeUsers dict example
#example: encrypt(activeUsers[user.email],"Thing to encrypt")
def encrypt(key, theThing, password=False):
    if password==True and theThing==("generate"):
        key = generate_key(key)
        theThing = generate_key()
        return Fernet(key).encrypt(theThing)

    if type(key)==str:
        key=key.encode('utf-8')

    if type(theThing)==str:
        theThing=theThing.encode('utf-8')

    return Fernet(key).encrypt(theThing)

# ─── ENCRYPTION ─────────────────────────────────────────────────────────────────

# Verifies the user and returns the User object if verified
# If verification failes it returns None
def verifyUser(email,password,addToActive=False):
    hashed_email = flask_scrypt.generate_password_hash(email, "")
    user = User.query.filter_by( email=hashed_email.decode("utf-8") ).first()

    pw = user.password.encode('utf-8')

    emailOK= hashed_email.decode('utf-8') == user.email  #boolean to compare with

    pwOK=flask_scrypt.check_password_hash(password, pw[:88], pw[88:176])

    if addToActive and (emailOK and pwOK):
            activeUsers[hashed_email]=decrypt(password.encode('utf-8'),user.enKey,True)

    if emailOK and pwOK:
        return True, user

    return False, None