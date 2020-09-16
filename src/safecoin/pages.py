from flask import render_template, flash, url_for, redirect
from safecoin import app

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")

#app.route('/overview')
#ef helloOverview():
#   return 'Hello from overview'

