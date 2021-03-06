from flask_login import UserMixin
import datetime
from sqlalchemy import DateTime

from safecoin import db, login_manager, redis


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

    # ─── LOGGED IN INFORMATION ──────────────────────────────────────────────────────
    # Due to how the sessions are set up, being logged in
    # does not mean you have access to change anything in the database
    # It only means having access to read data that is
    # currently in that users redis dictionary
    # The password is the only thing that allows a user to change data.

    # If the user is not found in redis,
    # the user is effectivly not logged in
    @property
    def is_authenticated(self):
        # Check if the current_user is logged in
        if redis.get(self.email):
            # If so set data to expire 10 minutes from now
            redis.expire(self.email, 900)

            # return true to the flask login manager
            return True
        return False

    # is active is for setting user status
    # For our use its technically not needed
    # can be set to true permanently
    # but possibly dangerous, so we will set it anyway
    @property
    def is_active(self):
        # Check if the current_user is logged in
        if redis.get(self.email):
            # If so set data to expire 10 minutes from now
            redis.expire(self.email, 900)

            # return true
            return True
        return False

    # ─── LOGGED IN INFORMATION ──────────────────────────────────────────────────────

    # login manager, defines user id must be unique
    def get_id(self):
        return self.email


class Account(db.Model):
    number = db.Column(db.String(11), unique=True, nullable=False, primary_key=True)
    balanceField = db.Column(db.String(256))  # tallet viser til maks lengde av et siffer

    # Henter verdien fra databasen og konverterer til streng
    @property
    def balance(self):
        return int(self.balanceField)

    # setter verdien i databasen, dersom den er en int, blir den til streng
    @balance.setter
    def balance(self, value):
        # Sjekker om jeg faar en int, ellers skal det ikke fungere.
        if type(value) == int:
            value = str(value)
            self.balanceField = value
        else:
            raise Exception("Can only set this to be an int")


class Transactions(db.Model):
    transactionID = db.Column(db.Integer, primary_key=True)
    accountFrom = db.Column(db.String(80), nullable=False)
    accountTo = db.Column(db.String(80), nullable=False, )
    amountDB = db.Column(db.String(256))
    message = db.Column(db.String(90))
    time = db.Column(DateTime, default=datetime.datetime.utcnow,nullable=False)
    # Henter verdien fra databasen og konverterer til streng

    @property
    def amount(self):
        return int(self.amountDB)

    # setter verdien i databasen, dersom den er en int, blir den til streng
    @amount.setter
    def amount(self, value):
        # Sjekker om jeg faar en int, ellers skal det ikke fungere.
        if type(value) == int:
            value = str(value)
            self.amountDB = value
        else:
            raise Exception("Can only set this to be an int")


class requestLogs(db.Model):
    eventID = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    email = db.Column(db.String(80))
    eventType = db.Column(db.String(64), nullable=False)  # what happened
    message = db.Column(db.String(300))
    time = db.Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
