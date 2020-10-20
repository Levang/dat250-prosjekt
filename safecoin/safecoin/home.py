from flask import render_template, url_for, redirect, request, flash
from flask_login import login_user, current_user, logout_user, login_required
### ------ Internal imports below ------ ###
from safecoin import app, db, bcrypt, redis, disable_caching
from safecoin.encryption import encrypt, decrypt, verifyUser

import pyotp
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
        # login=bool
        # userDB = Database class
        # Secret = 2fa Secret
        # returns true and other values only if user is registered in database.

        login, userDB, secret = verifyUser(form.email.data, form.password.data, addToActive=True)

        # ─── KOMMENTERES TILBAKE VED PRODUKSJON ──────────────────────────
        # try:
        #     login, userDB, secret = verifyUser(form.email.data,form.password.data,addToActive=True)
        # except:
        #     login=False
        #     flash('Something went wrong. Please try again.')
        # ─── KOMMENTERES TILBAKE VED PRODUKSJON ──────────────────────────

        if login:

            # sender secret key til 2FA klasse
            totp = pyotp.TOTP(secret)

            # Denne returnerer True hvis koden fra brukeren er overens med serveren. MERK: serveren sin
            if totp.verify(form.otp.data):
                # genererte totp er tilsynelatende omtrent 10 sekunder foran koden som brukeren genererer..
                login_user(userDB, remember=form.remember.data)

                # Redirect til overview dersom alt er ok
                return redirect(url_for("overviewPage")), disable_caching

        else:
            # Generisk feilmelding dersom noe går galt
            flash('Something went wrong. Please try again.')

    # dersom noe gaar galt rendre samme side
    return render_template("login.html", form=form), disable_caching


# If we need a method for a user to log out :
@app.route("/logout")
@login_required
def logout():
    #slett ifra redis først ellers er current_user ikke definert.
    redis.delete(current_user.email)

    #Logg så ut fra login manager
    logout_user()
    return redirect(url_for('home')), disable_caching
