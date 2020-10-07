from flask_login import UserMixin
from flask_scrypt import generate_password_hash
from safecoin import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(email=user_id).first()


class User(db.Model, UserMixin):
    email = db.Column(db.String(80), primary_key=True, unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    secret = db.Column(db.String(32 + 128))
    accounts = db.Column(db.String(10000))

    def get_id(self):
        return self.email


class Account(db.Model, UserMixin):
    number = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    pub_key = db.Column(db.String(300), unique=True, nullable=False)
    balance = db.Column(db.Numeric(80))
