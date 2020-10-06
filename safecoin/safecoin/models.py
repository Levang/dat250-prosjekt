from flask_login import UserMixin
from safecoin import db, login_manager


@login_manager.user_loader
def load_user(id):
    # TODO Levang must verify that this works.. Removed ids from user db for simplicity (wasn't needed)
    return User.query.get(id)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, unique=True)
    email = db.Column(db.String(120), primary_key=True, unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    accounts = db.Column(db.String(120))
    acc_hashed = db.Column(db.String(80))


class Account(db.Model, UserMixin):
    accountNumber = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    balance = db.Column(db.Float, default=0.0)
