from flask_login import current_user
from random import randint

from safecoin import db
from safecoin.models import Account, User
from safecoin.encryption import decrypt, encrypt, redis_sync

# --- Gets account objects --- #

def getAccount(account_number):
    account: Account = Account.query.filter_by(number=account_number).first()
    return account


def getUser(email):
    user: User = User.query.filter_by(email=email).first()
    return user


def getCurrentUser():
    user: User = getUser(current_user.email)
    return user

# ---------------------------- #


# "name,accountnumber,secretKey;name2,accountnumber2,secretKey2;"
# Converts into list of lists:
# [[name, accountnumber, secretKey], [name2, accountnumber2, secretKey2]]
def accStr_to_accList(accStr: str):
    accList = accStr.split(";")
    while accList and accList[-1] == "":
        accList.pop()
    newList = []
    for account in accList:
        tmpList = []
        entryList = account.split(",")
        for entry in entryList:
            tmpList.append(entry)
        newList.append(tmpList)
    return newList


# [[name1, num1, key1], [name2, num2, key2]] -> "name1,num1,key1;name2,num2,key2;"
def accList_to_accStr(accList: iter):
    newStr = ""
    for account in accList:
        newStr += ",".join(account)
        newStr += ";"
    return newStr


def format_account_number(number: int):
    try:
        acc_str = str(number)
        return f"{acc_str[:4]}.{acc_str[4:6]}.{acc_str[6:]}"
    except TypeError:
        return number


def getAccountNumber():
    while True:
        bank_id = str(randint(4100, 4300))
        account_type = "69"
        customer_acc = str(randint(1000, 9999))
        acc_num_without_redundancy = bank_id + account_type + customer_acc
        temp = int(acc_num_without_redundancy)
        redundancy_num = str(temp % 10)
        account_number = acc_num_without_redundancy + redundancy_num
        if not Account.query.filter_by(number=account_number).first():
            if len(str(account_number)) != 11:
                raise Exception(f"{account_number}'s length isn't 11!")
            return account_number


def addNewAccountToCurUser(password, name="My account"):
    user = current_user
    account = Account(number=getAccountNumber(), balance=0, pub_key=f"pubkey{randint(0, 1000000)}")

    #Characters allowed in the name
    alphabet="abcdefghijklmnopqrstuvwxyzæøå0123456789 "

    #Transform name to lowercase and check if its not in the alphabet
    print(f"---->{name}<---")
    for letter in name.lower():
        if letter not in alphabet:
            return "Couldn't create account with the given name"

    #Decrypt the encryption key
    enKey = decrypt(password, user.enKey.encode('utf-8'), True)

    #Attempt decryption of the users accounts
    if user.accounts==None:
        accountsListSplit1 = ""
        accountsFromDB=""
    else:
        #THIS IS ALLWAYS A STRING NOTHING BUT A STRING TO/FROM DATABASE
        accountsFromDB = decrypt(enKey, user.accounts).decode('utf-8')
        #split them  into each account
        accountsListSplit1 = accountsFromDB.split(";")

    #Max amount of accounts
    if len(accountsListSplit1) > 25:
        return "Couldn't create account, because number of accounts can't exceed 25"

    #Split the accounts again this is now a list of lists
    for accountsListSplit2 in accountsListSplit1:
        cur_acc_list = accountsListSplit2.split(",")

        #check if the account name exists
        if cur_acc_list[0].upper() == name.upper():
            return "Couldn't create account with the given name"

    # Max length of your account name
    # 24 is plenty
    # Site look and feel is broken by long name
    if len(name) > 24:
        return "Couldn't create account with the given name, name is too long"

    # Encrypt the informaton
    NEWaccountsStr=f"{accountsFromDB}{name},{account.number},privatekey{randint(0, 1000000)};"
    encryptedAccounts = encrypt(enKey,NEWaccountsStr)

    user.accounts=encryptedAccounts.decode('utf-8')
    # Save the stuff.
    db.session.add(account)
    db.session.add(user)
    db.session.commit()
    redis_sync(enKey,current_user.email)


def deleteCurUsersAccountNumber(account_number: str, password):
    user = getCurrentUser()
    account = getAccount(account_number)
    if account.balance != 0:
        return "Couldn't delete account with a balance not equal to 0.0"
    enKey = decrypt(password, user.enKey, True)
    accStr = decrypt(enKey, user.accounts).decode("utf-8")
    accList = accStr_to_accList(accStr)
    for acc in accList:
        print(f'accnr {acc[1]} {account_number}')
        print(f'accnr {type(acc[1])} {type(account_number)}')

        if int(acc[1]) == account_number:
            print("JEG ER HER")
            accList.remove(acc)
            newAccStr = accList_to_accStr(accList)
            print(newAccStr)
            user.accounts = encrypt(enKey, newAccStr).decode('utf-8')
            #db.session.delete(account)
            db.session.commit()
            redis_sync(enKey,current_user.email)
            return
    return "Couldn't delete the given account"

