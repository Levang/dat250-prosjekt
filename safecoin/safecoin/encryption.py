import base64, json, pyotp
from cryptography.fernet import Fernet
import flask_scrypt, scrypt
from flask_login import current_user
from safecoin.models import User
from safecoin import redis
from flask_login import current_user

# ─── ENCRYPTION ─────────────────────────────────────────────────────────────────
def generate_key(password=''):
    if password == '':
        return Fernet.generate_key()

    if type(password) == bytes:
        password = password.decode('utf-8')

    password = password.encode('utf-8')

    key = scrypt.hash(password, salt='', N=2 ** 16, r=8, p=1, buflen=32)
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
        key = generate_key(key)  # DETTE ER PASSORD
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
    if accInput == None:
        return None

    if type(accInput) != str:
        accInput = accInput.decode('utf-8')

    out = {}
    split_again = accInput.split(';')
    for i in split_again:
        if len(i) > 11:
            nameAccount = i.split(',')
            out[nameAccount[1]] = [nameAccount[0]]
    return out


def verifyUser(email, password, addToActive=False):
    # hash the email
    hashed_email = flask_scrypt.generate_password_hash(email, "")

    # create user class with information from database
    userDB = User.query.filter_by(email=hashed_email).first()

    # if the user doesnt exist in database
    if userDB is None:
        return False, None, None

    # format password from database
    DBpw = userDB.password.encode('utf-8')

    # check if the hashed email is the same ass the one in the database, just a double check.
    # Strictly not nececairy, but just seems logical to do.
    emailOK = hashed_email.decode('utf-8') == userDB.email.decode('utf-8')  # boolean to compare with

    # Verify that the password is correct
    pwOK = flask_scrypt.check_password_hash(password.encode('utf-8'), DBpw[:88], DBpw[88:176])

    if emailOK and pwOK:
        # decrypte the users encryption key
        decryptKey = decrypt(password, userDB.enKey.encode('utf-8'), True)

        # Decrypt the secret key
        secret_key = decrypt(decryptKey, userDB.secret.encode('utf-8'))

        # Check if the password is correct and email exists in the database
        if addToActive:
            # create user dict for json dump
            userInfo = {}
            # Add plaintext email as a key
            userInfo['email'] = email

            # Check if user has any accounts
            if userDB.accounts != None:
                # if so decrypt them
                accounts = decrypt(decryptKey, userDB.accounts.encode('utf-8'))

                # add them to the dictionary of the user
                userInfo['accounts'] = DBparseAccounts(accounts)

            # convert the dictionary into a string
            userInfo = json.dumps(userInfo)

            # add it to the redis database
            redis.set(hashed_email, userInfo)
            # set the expiration time of the data added
            # 900 seconds= 15 minutes
            redis.expire(hashed_email, 900)

        # In case any errors occur above we do not add.
        if emailOK and pwOK:
            return True, userDB, secret_key

    return False, None, None


# This just encodes everything in a dict into a string
# Used in register to convert information for redis server
def dictToStr(dictionary):
    for i in dictionary:
        if type(dictionary[i]) != str:
            dictionary[i] = dictionary[i].decode('utf-8')

    return json.dumps(dictionary)


# Return current users email in clear text
def getCurUsersEmail():
    user_dict = json.loads(redis.get(current_user.email))
    return user_dict['email']


# Verify password, 2fa(otp) against email. Defaults to current email
def verify_pwd_2FA(password, otp, email=None):
    # Set email to current if email isn't set
    if not email:
        email = getCurUsersEmail()
    # Verifies password
    is_authenticated, user, secret = verifyUser(email, password)
    if is_authenticated:
        # Verifies 2fa
        totp = pyotp.TOTP(secret)
        if totp.verify(otp):
            return True, user
    return False, None

#Sync redis with database
def redis_sync(deKey,hashed_mail):
    if type(deKey)==str:
        deKey=deKey.encode('utf-8')
    #Get user from database
    userDB = User.query.filter_by(email=hashed_mail).first()

    #create user dict for json dump
    userInfo = {}

    #Add plaintext email as a key
    #Check if its a string
    if type(userDB.enEmail)==str:
        userInfo['email'] = decrypt(deKey, userDB.enEmail.encode('utf-8')).decode('utf-8')
    else:
         userInfo['email'] = decrypt(deKey, userDB.email).decode('utf-8')

    #If the user has any accounts
    if userDB.accounts != None:
        #decrypt them
        if type(userDB.accounts)==str:
            accounts = decrypt(deKey, userDB.accounts.encode('utf-8'))
        else:
            accounts = decrypt(deKey, userDB.accounts)

        #add them to the dictionairy of the user
        userInfo['accounts'] = DBparseAccounts(accounts)

    userInfo = json.dumps(userInfo)
    #add it to the redis database

    redis.set(userDB.email, userInfo)
    #set the expiration time of the data added
    #900 seconds= 15 minutes
    redis.expire(userDB.email,900)
