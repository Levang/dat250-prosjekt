from safecoin.models import requestLogs
from safecoin import db


def log(message: str = "NA", eventType: str = "NA", hashedEmail: str = "NA"):
    try:
        req = requestLogs(message=message, eventType=eventType, email=hashedEmail)
        db.session.add(req)
        db.session.commit()
    except:
        req = requestLogs(message="NA", eventType="loggingerror", email="NA")
        db.session.add(req)
        db.session.commit()


def log_loginattempt(is_validated: bool, hashedEmail: str):
    msg = "Validated:"
    if is_validated:
        msg += "YES"
    else:
        msg += "NO"
    log(msg, "loginattempt", hashedEmail)


def log_logout(hashedEmail: str):
    log(eventType="logout", hashedEmail=hashedEmail)


def log_register(is_validated: bool, hashedEmail: str):
    msg = "Created:"
    if is_validated:
        msg += "YES"
    else:
        msg += "NO"

    log(msg, "register", hashedEmail)


def log_startregister(hashedEmail: str):
    log(eventType="startregister", hashedEmail=hashedEmail)


def log_createaccount(is_validated: bool, hashedEmail: str = "NA", accountNumber: str = "", custommsg: str = ""):
    msg = "Created:"
    if is_validated:
        msg += "YES"
    else:
        msg += "NO"

    if accountNumber:
        msg += f"|Number:{accountNumber}"

    if custommsg:
        msg += f"|Message:{custommsg}"

    log(msg, "createaccount", hashedEmail)


def log_deleteaccount(is_validated: bool, hashedEmail: str = "NA", accountNumber: str = "", custommsg: str = ""):
    msg = "Deleted:"
    if is_validated:
        msg += "YES"
    else:
        msg += "NO"

    if accountNumber:
        msg += f"|Number:{accountNumber}"

    if custommsg:
        msg += f"|Message:{custommsg}"

    log(msg, "deleteaccount", hashedEmail)


def log_deleteuser(is_validated: bool, hashedEmail: str = "NA", custommsg: str = ""):
    msg = "Deleted:"
    if is_validated:
        msg += "YES"
    else:
        msg += "NO"

    if custommsg:
        msg += f"|Message:{custommsg}"

    log(msg, "deleteuser", hashedEmail)


def log_transfer(is_validated: bool, from_: str = "", to: str = "", kid: str = "", amount: int = 0, hashedEmail: str = "NA", custommsg: str = ""):
    msg = "Transferred:"
    if is_validated:
        msg += "YES"
    else:
        msg += "NO"

    if from_:
        msg += f"|From:{from_}"

    if to:
        msg += f"|To:{to}"

    if kid:
        msg += f"|KID:{kid}"

    if amount:
        msg += f"|Amount:{amount}"

    if custommsg:
        msg += f"|Message:{custommsg}"

    log(msg, "transaction", hashedEmail)
