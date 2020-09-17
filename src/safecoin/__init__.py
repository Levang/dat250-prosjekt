from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.secret_key = "i am a potato"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Path for database
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from safecoin import home
from safecoin import overview
from safecoin import register
