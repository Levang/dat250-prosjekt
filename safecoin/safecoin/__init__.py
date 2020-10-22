from flask import Flask
from flask_sqlalchemy import SQLAlchemy
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
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RECAPTCHA_USE_SSL'] = True
app.config['RECAPTCHA_PUBLIC_KEY'] = '6Ldn29kZAAAAABFDZuYicPzQg5y8Kx5-DD-I_F62'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6Ldn29kZAAAAAHxWe2VkfSMpE-HN-YKCV2uA7CA_'

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


