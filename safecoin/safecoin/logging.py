from safecoin.models import requestLogs
from safecoin import db


def log(message: str = "NA", eventType: str = "NA", hashedEmail: str = "NA"):
    req = requestLogs(message=message, eventType=eventType, email=hashedEmail)
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
