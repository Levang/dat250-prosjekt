import hashlib, base64, json
from cryptography.fernet import Fernet
import flask_scrypt
from safecoin.models import User
from safecoin import redis


class UserClass:
    email = ''
    accounts = ''
    secret = ''




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

def DBparseAccounts(accInput):
    if type(accInput) != str:
        accInput=accInput.decode('utf-8')
        print(accInput)

    out={}
    split_again=accInput.split(';')
    for i in split_again:
        nameAccount=i.split(',')
        out[nameAccount[1]]=[nameAccount[0]]
    return out

def verifyUser(email,password,addToActive=False):
    hashed_email = flask_scrypt.generate_password_hash(email, "")
    userDB = User.query.filter_by( email=hashed_email.decode("utf-8") ).first()

    pw = userDB.password.encode('utf-8')

    emailOK= hashed_email.decode('utf-8') == userDB.email  #boolean to compare with

    pwOK=flask_scrypt.check_password_hash(password, pw[:88], pw[88:176])

    if addToActive and (emailOK and pwOK):
        decryptKey=decrypt(password.encode('utf-8'),userDB.enKey,True)

        userInfo={}
        userInfo['email']=email

        if userDB.accounts != None:
            accounts = decrypt(decryptKey,userDB.accounts)
            userInfo['accounts'] = DBparseAccounts(accounts)
            userInfo=json.dumps(userInfo)


        redis.set(hashed_email,userInfo)

    if emailOK and pwOK:
        return True, userDB

    return False, None



