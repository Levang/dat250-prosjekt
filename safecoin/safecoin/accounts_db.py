from flask_login import current_user
from random import randint

from safecoin import db
from safecoin.models import Account, User
from safecoin.encryption import decrypt, encrypt, redis_sync, illegalChar, verify_pwd_2FA
from safecoin.logging import log_createaccount, log_deleteaccount


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


def format_account_balance(balance: int):
    if balance < 10:
        return f"0,0{balance}"
    elif balance < 100:
        return f"0,{balance}"
    else:
        balance = str(balance)
        return f'{balance[:-2]},{balance[-2:]}'


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


def addNewAccountToCurUser(password, otp, name="My account", user=None, money=False, isCurrentUser=True):
    if isCurrentUser:
        authenticated, _ = verify_pwd_2FA(password, otp)
        if not authenticated:
            try:
                log_createaccount(False, current_user.email, custommsg="NotAuthenticated")
            except:
                log_createaccount(False, custommsg="NotAuthenticated")
            return "Couldn't create account due to an error"

    if user is None:
        user = current_user

    enKey = decrypt(password, user.enKey.encode('utf-8'), True)

    # 100000 er 1000.00 kr int er altsaa bare to ekstra nuller
    if money is True:
        account = Account(number=getAccountNumber(), balance=100000)
    else:
        account = Account(number=getAccountNumber(), balance=0)

    # Max length of your account name
    # 24 is plenty
    # Site look and feel is broken by long name
    # Checks for illegal characters and length
    if illegalChar(name, 24):
        log_createaccount(False, user.email, account.number, "BadName")
        return "Couldn't create account with the given name"

    # Attempt decryption of the users accounts
    if user.accounts is None:
        accountsListSplit1 = ""
        accountsFromDB = ""
    else:
        # THIS IS ALWAYS A STRING NOTHING BUT A STRING TO/FROM DATABASE
        accountsFromDB = decrypt(enKey, user.accounts).decode('utf-8')
        # split them  into each account
        accountsListSplit1 = accountsFromDB.split(";")

    # Max amount of accounts
    if len(accountsListSplit1) > 25:
        log_createaccount(False, user.email, account.number, "TooManyAccounts")
        return "Couldn't create account, because number of accounts can't exceed 25"

    # Split the accounts again this is now a list of lists
    for accountsListSplit2 in accountsListSplit1:
        cur_acc_list = accountsListSplit2.split(",")

        # check if the account name exists
        if cur_acc_list[0].upper() == name.upper():
            log_createaccount(False, user.email, account.number, "BadName")
            return "Couldn't create account with the given name"

    # Encrypt the information
    NEWaccountsStr = f"{accountsFromDB}{name},{account.number},privatekey{randint(0, 1000000)};"
    encryptedAccounts = encrypt(enKey, NEWaccountsStr)

    user.accounts = encryptedAccounts.decode('utf-8')
    # Save the stuff.
    db.session.add(account)
    db.session.add(user)
    db.session.commit()
    redis_sync(enKey, user.email)
    log_createaccount(True, user.email, account.number, f"(Balance:{account.balance}kr)(Name:{name})")


def deleteCurUsersAccountNumber(account_number: str, password, otp):
    # Return error if password or otp is wrong
    authenticated, user = verify_pwd_2FA(password, otp)
    if not authenticated:
        try:
            log_deleteaccount(False, current_user.email, account_number, "NotAuthenticated")
        except:
            log_deleteaccount(False, accountNumber=account_number, custommsg="NotAuthenticated")
        return "Couldn't delete account due to an error"

    account = getAccount(account_number)
    if account.balance != 0:
        log_deleteaccount(False, user.email, account_number, "AccountNotEmpty")
        return "Couldn't delete account with a balance not equal to 0.0"
    enKey = decrypt(password, user.enKey, True)
    accStr = decrypt(enKey, user.accounts).decode("utf-8")
    accList = accStr_to_accList(accStr)
    for acc in accList:
        if int(acc[1]) == account_number:
            accList.remove(acc)
            newAccStr = accList_to_accStr(accList)
            user.accounts = encrypt(enKey, newAccStr).decode('utf-8')
            db.session.commit()
            redis_sync(enKey, current_user.email)
            log_deleteaccount(True, user.email, account_number, f"(Name:{acc[0]})")
            return
    log_deleteaccount(False, user.email, account_number)
    return "Couldn't delete the given account"
