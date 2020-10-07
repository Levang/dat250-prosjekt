from flask import render_template, url_for, redirect, request, flash
from configparser import ConfigParser
###################
from safecoin import app, db, bcrypt
import flask_scrypt
from safecoin.models import User
from safecoin.forms import RegistrationForm
from safecoin.accounts import addNewAccountToUser
# db.create_all()


def isCommonPassword(password):
    with open("safecoin/commonPasswords.txt", "r") as f:
        for weakpwd in f:
            if password == weakpwd[:-1]:
                return True
    return False


def getPasswordViolations(errList, password):
    if type(password) != str:
        errList.append("An error occured!")
        return

    if isCommonPassword(password):
        errList.append("Password is too common")
        return

    # Password params
    cfg = ConfigParser()
    cfg.read("safecoin/config.ini")
    policy = cfg["passwordPolicy"]
    try:
        want_length = int(policy["length"])
    except (KeyError, TypeError):
        want_length = 10

    if len(password) < want_length:
        errList.append(f"Password should be at least {want_length} characters")


# --- Register page --- #
#@app.route("/register/")
#def register():
#    return render_template("register.html")


@app.route("/register/", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        errList = []
        getPasswordViolations(errList, form.password.data)
        if len(errList) == 0:
            hashed_email = flask_scrypt.generate_password_hash(form.email.data, "")
            print(hashed_email)

            salt = flask_scrypt.generate_random_salt()
            print(salt)

            hashed_pw = flask_scrypt.generate_password_hash(form.password.data, salt)
            print(hashed_pw)

            if User.query.filter_by(email=hashed_email.decode("utf-8")).first():
                flash("error")
                return render_template("register.html", form=form)


            user = User(email=hashed_email.decode("utf-8"), password=(hashed_pw+salt).decode("utf-8"))
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You are now able to log in.', 'success')
            return redirect(url_for('home'))
        for err in errList:
            flash(err, "error")
    return render_template("register.html", form=form)
