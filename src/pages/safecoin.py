from flask import Flask, render_template, flash, url_for, redirect

from . import *
app = Flask(__name__)

login.login()
register.register()
contact.contact()

if __name__ == "__main__":
    app.run(debug=True)
