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
    if password == '':
        return Fernet.generate_key()

    if type(password) == bytes:
        password = password.decode('utf-8')

    password = password.encode('utf-8')

    # NOTTODO fuck off, MD5 is broken
    # NO you fuck off, please take some time to understand what this function is doing.
    # Not a security feature.
    key = hashlib.md5(password).hexdigest().encode('utf-8')
    key = base64.urlsafe_b64encode(key)
    return key


# Used with the activeUsers dict example
# example: decrypt(activeUsers[user.email],"Thing to decrypt")
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


# Used with the activeUsers dict example
# example: encrypt(activeUsers[user.email],"Thing to encrypt")
def encrypt(key, theThing, password=False):
    if password and theThing == ("generate"):
        key = generate_key(key) #DETTE ER PASSORD
        theThing = generate_key()
        return Fernet(key).encrypt(theThing)

    if type(key) == str:
        key = key.encode('utf-8')

    if type(theThing) == str:
        theThing = theThing.encode('utf-8')

    print(key)
    print(theThing)
    return Fernet(key).encrypt(theThing)


# ─── ENCRYPTION ─────────────────────────────────────────────────────────────────

# Verifies the user and returns the User object if verified
# If verification failes it returns None

def DBparseAccounts(accInput):
    if type(accInput) != str:
        accInput = accInput.decode('utf-8')
        # print(accInput)

    out = {}
    split_again = accInput.split(';')
    for i in split_again:
        if len(i) > 11:
            nameAccount = i.split(',')
            out[nameAccount[1]] = [nameAccount[0]]
    return out


def verifyUser(email, password, addToActive=False):
    hashed_email = flask_scrypt.generate_password_hash(email, "")
    userDB = User.query.filter_by(email=hashed_email).first()
    print('CHECK DATABASE')
    print(userDB)


    pw = userDB.password.encode('utf-8')

    emailOK = hashed_email.decode('utf-8') == userDB.email.decode('utf-8')  # boolean to compare with

    pwOK = flask_scrypt.check_password_hash(password.encode('utf-8'), pw[:88], pw[88:176])
    print('CHECK PASSWORD')
    print(pwOK)
    print('CHECK EMAIL OK')
    print(emailOK)


    if addToActive and (emailOK and pwOK):
        decryptKey = decrypt(password, userDB.enKey.encode('utf-8'), True)

        userInfo = {}
        userInfo['email'] = email
        secret_key = decrypt(decryptKey, userDB.secret.encode('utf-8'))

        if userDB.accounts != None:
            accounts = decrypt(decryptKey, userDB.accounts.encode('utf-8'))

            userInfo['accounts'] = DBparseAccounts(accounts)


        userInfo = json.dumps(userInfo)

        redis.set(hashed_email, userInfo)
        redis.expire(hashed_email,900)

    if emailOK and pwOK:
        return True, userDB, secret_key

    return False, None, None




def dictToStr(dictionairy):
    for i in dictionairy:
        if type(dictionairy[i])!=str:
            dictionairy[i]=dictionairy[i].decode('utf-8')

    return json.dumps(dictionairy)
