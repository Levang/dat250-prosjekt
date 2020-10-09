from flask import Flask
from flask import redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from configparser import ConfigParser
from flask_redis import FlaskRedis
import json

cfg = ConfigParser()
cfg.read("safecoin/config.ini")

app = Flask(__name__)
app.secret_key = cfg["flask"]["secret_key"]
app.config['SQLALCHEMY_DATABASE_URI'] = cfg["sqlDb"]["path"]  # Path for database
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
redis = FlaskRedis(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/login'


from safecoin import home, overview, register, accounts, pay
