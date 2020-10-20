from flask_login import UserMixin
from flask_scrypt import generate_password_hash
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
    # currently in that users redis dictionairy
    # The password is the only thing that allows a user to change data.

    # If the user is not found in redis,
    # the user is effectivly not logged in
    @property
    def is_authenticated(self):
        # Check if the current_user is logged in
        if redis.get(self.email):
            # If so set data to expire 10 minutes from now
            redis.expire(self.email, 3600)

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
            redis.expire(self.email, 3600)

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
    pub_key = db.Column(db.String(300), unique=True, nullable=False)

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
    accTo = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    accFrom = db.Column(db.String(80), unique=True, nullable=False)
    amount = db.Column(db.Numeric(256))
    message = db.Column(db.String(300), )
    time = db.Column(db.String(80), nullable=False)
    eventID = db.Column(db.String(80), unique=True, nullable=False)
    signature = db.Column(db.String(300), unique=True,
                          nullable=False)  # dunno how long this should be but leaving it at 300 for now


class requestLogs(db.Model):
    time = db.Column(db.String(80), unique=False, nullable=False, primary_key=True)
    eventID = db.Column(db.String(80), unique=True, nullable=False)
    eventType = db.Column(db.String(64), unique=True, nullable=False)  # what happend
    message = db.Column(db.String(300))
    signature = db.Column(db.String(300), unique=True,
                          nullable=False)  # dunno how long this should be but leaving it at 300 for now
