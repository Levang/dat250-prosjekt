from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db' # Path for database
db = SQLAlchemy(app)

from safecoin import pages
from safecoin import overview
