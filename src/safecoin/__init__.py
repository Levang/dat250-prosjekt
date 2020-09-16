from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "i am a potato"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Path for database
db = SQLAlchemy(app)

from safecoin import pages
from safecoin import overview
from safecoin import register
