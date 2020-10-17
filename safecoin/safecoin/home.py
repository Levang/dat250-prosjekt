from flask import render_template, url_for, redirect, request, flash
from flask_login import login_user, current_user, logout_user, login_required
### ------ Internal imports below ------ ###
from safecoin import app, db, bcrypt
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

        login , userDB = verifyUser(form.email.data,form.password.data,addToActive=True)
        if login:
# ------------ 2 faktor på login -----------------#
                                                #TODO
            totp = pyotp.TOTP(userDB.secret)    #Må dekryptere secretkey her, AKA userDB.secret inni den totp variabelen må være den ukrypterte
            if totp.verify(form.otp.data)       #Denne returnerer True hvis koden fra brukeren er overens med serveren. MERK: serveren sin 
                                                #genererte totp er tilsynelatende omtrent 10 sekunder foran koden som brukeren genererer..
                login_user(userDB, remember=form.remember.data)
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
