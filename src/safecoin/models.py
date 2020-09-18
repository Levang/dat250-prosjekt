from flask_login import UserMixin
from safecoin import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    accounts = db.Column(db.String(12*10-1))


class Account(db.Model, UserMixin):
    account_num = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    balance = db.Column(db.Float, default=0.0)
    # TODO: Add column for users email/id?
