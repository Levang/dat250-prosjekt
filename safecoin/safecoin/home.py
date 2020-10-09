from flask import render_template, url_for, redirect, request, flash
from flask_login import login_user, current_user, logout_user, login_required
### ------ Internal imports below ------ ###
from safecoin import app, db, bcrypt, activeUsers
from safecoin.encryption import encrypt, decrypt, verifyUser

import flask_scrypt
from safecoin.models import User
from safecoin.forms import LoginForm
from safecoin.overview import overviewPage


# --- Main page --- #
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def home():
    form = LoginForm()
    if form.validate_on_submit():

        login, user = verifyUser(form.email.data, form.password.data, addToActive=True)
        if login:
            login_user(user, remember=form.remember.data)
            return redirect(url_for("overviewPage"))
        else:
            flash('Wrong username or password. Please try again.')
    return render_template("login.html", form=form)


# If we need a method for a user to log out:
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
