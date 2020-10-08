from flask_login import UserMixin
from flask_scrypt import generate_password_hash
from safecoin import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(email=user_id).first()


class User(db.Model, UserMixin):
    email = db.Column(db.String(80), primary_key=True, unique=True, nullable=False)
    enEmail = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    enKey = db.Column(db.String(128))
    accounts = db.Column(db.String(10000))
    secret = db.Column(db.String(32 + 128))


    def get_id(self):
        return self.email


class Account(db.Model):
    number = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    balance = db.Column(db.Numeric(256)) #tallet viser til maks lengde av et siffer
    pub_key = db.Column(db.String(300), unique=True, nullable=False)


class Transactions(db.Model):
    accTo = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    accFrom = db.Column(db.String(80), unique=True, nullable=False)
    amount = db.Column(db.Numeric(256))
    message = db.Column(db.String(300),)
    time = db.Column(db.String(80), nullable=False)
    eventID = db.Column(db.String(80), unique=True, nullable=False)
    signature = db.Column(db.String(300), unique=True, nullable=False) #dunno how long this should be but leaving it at 300 for now


class requestLogs(db.Model):
    time = db.Column(db.String(80), unique=False, nullable=False,primary_key=True)
    eventID = db.Column(db.String(80), unique=True, nullable=False)
    eventType = db.Column(db.String(64), unique=True, nullable=False) #what happend
    message = db.Column(db.String(300))
    signature = db.Column(db.String(300), unique=True, nullable=False) #dunno how long this should be but leaving it at 300 for now


