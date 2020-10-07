from flask import render_template, url_for, redirect, request, flash
from flask_login import login_user, current_user, logout_user, login_required
### ------ Internal imports below ------ ###
from safecoin import app, db, bcrypt
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
        hashed_email = flask_scrypt.generate_password_hash(form.email.data, "")
        print(hashed_email)

        user = User.query.filter_by(email=hashed_email.decode("utf-8")).first()

        if not user:
            flash('Wrong username or password. Please try again.')
            return render_template("login.html", form=form)

        pw = bytes(user.password, "utf-8")

        pw_hash = pw[:88]
        print(pw_hash)

        pw_salt = pw[88:176]
        print(pw_salt)

        if user and flask_scrypt.check_password_hash(form.password.data, pw_hash, pw_salt):
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




