import base64, json, pyotp
from cryptography.fernet import Fernet, InvalidToken
import flask_scrypt, scrypt
from flask_login import current_user
from safecoin.models import User, Account, Transactions
from safecoin import redis, db
from flask_login import current_user


# ─── GENERATE KEY ─────────────────────────────────────────────────────────────────
def generate_key(password=''):
    if password == '':
        return Fernet.generate_key()

    if type(password) == bytes:
        password = password.decode('utf-8')

    password = password.encode('utf-8')

    key = scrypt.hash(password, salt='', N=2 ** 16, r=8, p=1, buflen=32)
    key = base64.urlsafe_b64encode(key)
    return key


# ─── DECRYPT THE INFORMATION ────────────────────────────────────────────────────
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


# ─── ENCRYPT THE INFORMATION ────────────────────────────────────────────────────
# Used with the activeUsers dict example
# example: encrypt(activeUsers[user.email],"Thing to encrypt")
def encrypt(key, theThing, password=False):
    if password and theThing == "generate":
        key = generate_key(key)  # DETTE ER PASSORD
        theThing = generate_key()
        return Fernet(key).encrypt(theThing)

    if type(key) == str:
        key = key.encode('utf-8')

    if type(theThing) == str:
        theThing = theThing.encode('utf-8')

    return Fernet(key).encrypt(theThing)


# ─── PARSE THE DATABASE ACCOUNTS AND SPLIT THEM ─────────────────────────────────
def DBparseAccounts(accInput):
    if accInput is None:
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


# ─── DICTIONARY TO STRING ──────────────────────────────────────────────────────
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

    # Convert otp from int to str and add 0 at the start. Keys starting with 0 now works.
    otp = str(otp)
    while len(otp) < 6:
        otp = "0" + otp

    # Verifies password
    try:
        is_authenticated, user, secret = verifyUser(email, password)
    except InvalidToken:
        return False, None

    if is_authenticated:
        # Verifies 2fa
        totp = pyotp.TOTP(secret)
        if totp.verify(otp):
            return True, user
    return False, None


# ─── REDIS SYNC ─────────────────────────────────────────────────────────────────
def redis_sync(deKey, hashed_mail):
    if type(deKey) == str:
        deKey = deKey.encode('utf-8')
    # Get user from database
    userDB = User.query.filter_by(email=hashed_mail).first()

    # create user dict for json dump
    userInfo = {}

    # Add plaintext email as a key
    # Check if its a string
    if type(userDB.enEmail) == str:
        userInfo['email'] = decrypt(deKey, userDB.enEmail.encode('utf-8')).decode('utf-8')
    else:
        userInfo['email'] = decrypt(deKey, userDB.email).decode('utf-8')

    # If the user has any accounts
    if userDB.accounts is not None:
        # decrypt them
        if type(userDB.accounts) == str:
            accounts = decrypt(deKey, userDB.accounts.encode('utf-8'))
        else:
            accounts = decrypt(deKey, userDB.accounts)

        # add them to the dictionairy of the user
        userInfo['accounts'] = DBparseAccounts(accounts)

    userInfo = json.dumps(userInfo)
    # add it to the redis database

    redis.set(userDB.email, userInfo)
    # set the expiration time of the data added
    # 900 seconds= 15 minutes
    redis.expire(userDB.email, 900)


# ─── GET ACCOUNT LIST ───────────────────────────────────────────────────────────
def getAccountsList(userDict=None):
    if current_user.accounts is None and userDict is None:
        return [['', 'Please open an account', '']]

    if userDict is None:
        userDict = redis.get(current_user.email)

    userDict = json.loads(userDict)

    i = 0
    account_list = []

    # Denne fungerer men må ryddes opp i, gjør det om til en funksjon elns.
    for accountnr in userDict['accounts']:
        numberUsr = int(accountnr)

        # Navnet ligger i 0te index [navn,kontonr,secret]
        name = userDict['accounts'][accountnr][0]

        # Hent kontobalanse fra accounts database
        accountDB = Account.query.filter_by(number=numberUsr).first()

        if accountDB:
            balance = accountDB.balance
            account_list.append([name, numberUsr, balance])
        else:
            return None

        i += 1
    return account_list


# ─── VERIFY USER ────────────────────────────────────────────────────────────────
def verifyUser(email, password, addToActive=False):
    # hash the email
    if email is None:
        hashed_email = current_user.email
    else:
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

    # Check if the password is correct and email exists in the database
    if emailOK and pwOK:

        # decrypte the users encryption key
        decryptKey = decrypt(password, userDB.enKey.encode('utf-8'), True)

        # Decrypt the secret key
        secret_key = decrypt(decryptKey, userDB.secret.encode('utf-8'))

        if addToActive:
            # sync with redis!
            redis_sync(decryptKey, hashed_email)

        return True, userDB, secret_key

    return False, userDB, None


# ─── SUBMIT A TRANSACTION ──────────────────────────────────────────────────────
# This only accepts current user.
def submitTransaction(password, accountFrom, accountTo, amount, message):
    accountFrom=str(accountFrom)
    accountTo=str(accountTo)
    #Check user password
    verified, userDB, ubrukt = verifyUser(None, password)

    if verified is False:
        return False
        #Decrypt and check user account with user database
    decryptKey = decrypt(password, userDB.enKey.encode('utf-8'), True)
    accountsDB = decrypt(decryptKey, userDB.accounts.encode('utf-8'))


    accountsDict = DBparseAccounts(accountsDB)

    #is the account one of the users accounts
    if str(accountFrom) in accountsDict:
                #if above checks out
                #do transfer
                accountDBFrom = Account.query.filter_by(number=accountFrom).first()
                accountDBTo = Account.query.filter_by(number=accountTo).first()

                if TransactionChecks(accountDBFrom, amount, accountDBTo, accountsDict,message)==False:
                    return False

                accountDBFrom.balance -= amount
                accountDBTo.balance += amount

                # LOGGING
                trans=Transactions()
                trans.accountTo = accountTo
                trans.accountFrom = accountFrom
                trans.amount = amount
                trans.message = message
                trans.eventID = 'transaction'


                db.session.add(accountDBFrom)
                db.session.add(accountDBTo)
                db.session.add(trans)
                db.session.commit()

                redis_sync(decryptKey,current_user.email)
                return True
                #add the transaction to the transaction history
    else:
        # user doesnt own this account return
        return False

        #sync redis

        #Make transactions page lookup function.


def TransactionChecks(accountFrom, amount, accountTo, accountsDict, message):
    #If internal transfer check that user balance remains unchanged
    #check for stuff
    if accountFrom==None or accountTo==None or accountFrom==accountTo:
        return False
    if amount<1 or type(amount)!=int or amount>accountFrom.balance:
        return False

    sumBefore=accountFrom.balance+accountTo.balance
    fromBalance = accountFrom.balance
    toBalance   = accountTo.balance
    fromAfter   = fromBalance - amount
    toAfter     = toBalance + amount

    sumAfter = fromAfter + toAfter

    if sumBefore!=sumAfter:
        return False

    if illegalChar(message,90):
        return False

    return True


def illegalChar(text, maxlength):
    if text==None:
        return False

    try:
        text=str(text)
    except:
        return True

    if len(text)>maxlength:
        return True

    alphabet="abcdefghijklmnopqrstuvwxyzæøå0123456789 "
    #Transform name to lowercase and check if its not in the alphabet
    for letter in text.lower():
        if letter not in alphabet:
            return True
    return False

