import base64, json
from cryptography.fernet import Fernet
import flask_scrypt, scrypt
from safecoin.models import User
from safecoin import redis
from flask_login import current_user

# ─── GENERATE KEY ─────────────────────────────────────────────────────────────────
def generate_key(password=''):
    if password == '':
        return Fernet.generate_key()

    if type(password) == bytes:
        password = password.decode('utf-8')

    password = password.encode('utf-8')

    key = scrypt.hash(password, salt='', N=2**16, r=8, p=1, buflen=32)
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


# ─── PARSE THE DATABASE ACCOUNTS AND SPLIT THEM ─────────────────────────────────
def DBparseAccounts(accInput):
    if accInput==None:
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

# ─── DICTIONAIRY TO STRING ──────────────────────────────────────────────────────
#This just encodes everything in a dict into a string
#Used in register to convert information for redis server
def dictToStr(dictionairy):
    for i in dictionairy:
        if type(dictionairy[i])!=str:
            dictionairy[i]=dictionairy[i].decode('utf-8')

    return json.dumps(dictionairy)


# ─── REDIS SYNC ─────────────────────────────────────────────────────────────────
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


# ─── GET ACCOUNT LIST ───────────────────────────────────────────────────────────
def getAccountsList(userDict):
    if current_user.accounts==None:
        return [['','Please open an account','']]

    if userDict==None:
        userDict = redis.get(current_user.email)

    userDict = json.loads(userDict)

    i = 0
    account_list = []

    #SJEKK OM ME FUCKER UP!

    # Denne fungerer men må ryddes opp i, gjør det om til en funksjon elns.
    for accountnr in userDict['accounts']:
        numberUsr = int(accountnr)

        #Navnet ligger i 0te index [navn,kontonr,secret]
        name = userDict['accounts'][accountnr][0]

        #Hent kontobalanse fra accounts database
        accountDB = Account.query.filter_by(number=numberUsr).first()

        if accountDB:
            balance = accountDB.balance
            # print(name)
            account_list.append([name, numberUsr, balance])
        else:
            return None

        i += 1
    return account_list



# ─── VERIFY USER ────────────────────────────────────────────────────────────────
def verifyUser(email, password, addToActive=False):
    #hash the email
    if email==None:
        hashed_email = flask_scrypt.generate_password_hash(email, "")
    else:
        hashed_email = current_user.email

    #create user class with information from database
    userDB = User.query.filter_by(email=hashed_email).first()

    #if the user doesnt exist in database
    if userDB==None:
        return False, None, None

    #format password from database
    DBpw = userDB.password.encode('utf-8')

    #check if the hashed email is the same ass the one in the database, just a double check.
    #Strictly not nececairy, but just seems logical to do.
    emailOK = hashed_email.decode('utf-8') == userDB.email.decode('utf-8')  # boolean to compare with

    #Verify that the password is correct
    pwOK = flask_scrypt.check_password_hash(password.encode('utf-8'), DBpw[:88], DBpw[88:176])

    #Check if the password is correct and email exists in the database
    if emailOK and pwOK:

        #decrypte the users encryption key
        decryptKey = decrypt(password, userDB.enKey.encode('utf-8'), True)

        #Decrypt the secret key
        secret_key = decrypt(decryptKey, userDB.secret.encode('utf-8'))

        if addToActive:
            #sync with redis!
            redis_sync(decryptKey,hashed_email)

        return True, userDB, secret_key

    return False, None, None



# ─── SUBMIT A TRANSACTION ──────────────────────────────────────────────────────
#This only accepts current user. 
def submitTransaction(password,accountFrom,accountTo,amount,message):
    print("INNE I SUBMIT TRANSACTIONS")

    #Check user password
    verified, userDB, _ = verifyUser(None,password)


    #Decrypt and check user account with user database
    decryptKey = decrypt(password, userDB.enKey.encode('utf-8'), True)
    accountsDB = decrypt(decryptKey, userDB.accounts.encode('utf-8'))

    accountsList = getAccountsList(DBparseAccounts(accountsDB))
    internalTransactionChecks(accountFrom, amount, accountTo, accountsList)

    #If external transfer
    externalTransactionChecks(accountFrom, amount, accountTo, accountsList)


    #if above checks out, do the transfer of the amount.

    #update database

    #sync redis

    #add the transaction to the transaction history

    #Make transactions page lookup function.

    return False


def internalTransactionChecks(accountFrom, accountTo):
    #If internal transfer check that user balance remains unchanged
    #check for stuff

    return False



def externalTransactionChecks(accountFrom, accountTo):
    #check for stuff
    #Check that total sum of both accounts balance remains unchanged.


    return False


