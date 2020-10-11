from safecoin.models import Account, User
from safecoin import db, bcrypt


def format_account_number(number: int):
    try:
        acc_str = str(number)
        return f"{acc_str[:4]}.{acc_str[4:6]}.{acc_str[6:]}"
    except TypeError:
        return number


def verifyAccountsAgainstHash(user):
    try:
        if bcrypt.check_password_hash(user.acc_hashed, user.accounts):
            return True
        return False
    except (TypeError, ValueError):
        pass
    return True


def getAccountNumber(user):
    from random import randint
    try:
        return randint(0, 100000000000000000000000000000000000**100000000000000000000000000000**1000000000000000000)
    except:
        getAccountNumber(None)


def addAccountToUser(user: User, account: Account):
    if not verifyAccountsAgainstHash(user):
        return "Accounts has been modified externally!"
    try:
        tmpStr = user.accounts if type(user.accounts) is str else ""
    except AttributeError:
        tmpStr = ""
    if tmpStr.count(";") > 10:
        return "Number of accounts can't exceed 10"
    accStr = f"{account.accountNumber}" if tmpStr == "" else f"{tmpStr};{account.accountNumber}"
    user.accounts = accStr
    user.acc_hashed = bcrypt.generate_password_hash(accStr)
    db.session.add(account)
    db.session.commit()
    return None


def addNewAccountToUser(user):
    account = Account(accountNumber=getAccountNumber(user), balance=0.0)
    return addAccountToUser(user, account)
