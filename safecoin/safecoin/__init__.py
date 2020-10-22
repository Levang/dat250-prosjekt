from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from configparser import ConfigParser
from flask_redis import FlaskRedis
from flask_qrcode import QRcode
from os import urandom

import json  # Don't remove this import ever!

cfg = ConfigParser()
cfg.read("safecoin/config.ini")

app = Flask(__name__)
app.secret_key = urandom(16)
app.config['SQLALCHEMY_DATABASE_URI'] = cfg["sqlDb"]["path"]  # Path for database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RECAPTCHA_USE_SSL'] = True
app.config['RECAPTCHA_PUBLIC_KEY'] = cfg["reCaptcha"]["site_key"]
app.config['RECAPTCHA_PRIVATE_KEY'] = cfg["reCaptcha"]["secret_key"]

db = SQLAlchemy(app)
redis = FlaskRedis(app)
QRcode(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/login'

disable_caching = {'Cache-Control': 'no-cache, no-store, must-revalidate',
                   'Pragma': 'no-cache',
                   'Express': '0'}


from safecoin import home, overview, register, accounts, pay, profile, hist_transfer, accounts_db, encryption


