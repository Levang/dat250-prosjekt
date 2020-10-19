from flask_login import current_user
from random import randint

from safecoin import db
from safecoin.models import Account, User
from safecoin.encryption import decrypt, encrypt


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


def addAccountToUser(user: User, account: Account, password, name="My account"):
    if ";" in name:
        return "Couldn't create account with the given name"
    enKey = decrypt(password, user.enKey, True)
    try:
        tmpStr = decrypt(enKey, user.accounts).decode("utf-8") if type(user.accounts) is bytes else ""
    except AttributeError:
        tmpStr = ""
    accountstr_list = tmpStr.split(";")
    if len(accountstr_list) > 50:
        return "Couldn't create account, because number of accounts can't exceed 50"
    for accountstr in accountstr_list:
        cur_acc_list = accountstr.split(",")
        if cur_acc_list[0].upper() == name.upper():
            return "Couldn't create account with the given name"
    if len(name) > 100:
        return "Couldn't create account with the given name"
    user.accounts = encrypt(enKey, f"{tmpStr}{name},{account.number},privatekey{randint(0, 1000000)};")
    db.session.add(account)
    db.session.commit()
#    sync_redis()


def addNewAccountToCurUser(account_name, password):
    account = Account(number=getAccountNumber(), balance=0.0, pub_key=f"pubkey{randint(0, 1000000)}")
    return addAccountToUser(getCurrentUser(), account, password, account_name)


def deleteCurUsersAccountNumber(account_number: str, password):
    user = getCurrentUser()
    account = getAccount(account_number)
    if account.balance != 0.0:
        return "Couldn't delete account with a balance not equal to 0.0"
    enKey = decrypt(password, user.enKey, True)
    accStr = decrypt(enKey, user.accounts).decode("utf-8")
    accList = accStr_to_accList(accStr)
    for acc in accList:
        if acc[1] == account_number:
            accList.remove(acc)
            newAccStr = accList_to_accStr(accList)
            print(newAccStr)
            user.accounts = encrypt(enKey, newAccStr)
            db.session.delete(account)
            db.session.commit()
            #sync_redis()
            return
    return "Couldn't delete the given account"
