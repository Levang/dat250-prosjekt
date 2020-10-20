from flask import Flask, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from configparser import ConfigParser
from flask_redis import FlaskRedis
from flask_qrcode import QRcode
import json

cfg = ConfigParser()
cfg.read("safecoin/config.ini")

app = Flask(__name__)
app.secret_key = cfg["flask"]["secret_key"]
app.config['SQLALCHEMY_DATABASE_URI'] = cfg["sqlDb"]["path"]  # Path for database
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
redis = FlaskRedis(app)
QRcode(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/login'

disable_caching = {'Cache-Control': 'no-cache, no-store, must-revalidate',
                   'Pragma': 'no-cache',
                   'Expres': '0'}


@app.after_request
def rem_cache(r):

    return r


from safecoin import home, overview, register, accounts, pay, profile, hist_transfer, transfer
