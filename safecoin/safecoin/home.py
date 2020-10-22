from flask import render_template, url_for, redirect, flash
from flask_login import login_user, current_user, logout_user, login_required
import pyotp

from safecoin import app, redis, disable_caching
from safecoin.encryption import verifyUser
from safecoin.forms import LoginForm
from safecoin.logging import log_loginattempt, log_logout


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
        # ─── KOMMENTERES TILBAKE VED PRODUKSJON ──────────────────────────

        # Convert otp from int to str and add 0 at the start. Keys starting with 0 now works.
        form.otp.data = str(form.otp.data)
        while len(form.otp.data) < 6:
            form.otp.data = "0" + form.otp.data

        if login:

            # sender secret key til 2FA klasse
            totp = pyotp.TOTP(secret)

            # Denne returnerer True hvis koden fra brukeren er overens med serveren. MERK: serveren sin
            if totp.verify(form.otp.data):
                log_loginattempt(True, userDB.email)
                # genererte totp er tilsynelatende omtrent 10 sekunder foran koden som brukeren genererer..
                login_user(userDB)

                # Redirect til overview dersom alt er ok
                return redirect(url_for("overviewPage")), disable_caching

            else:
                # Generisk feilmelding dersom noe går galt
                flash('Something went wrong. Please try again.')
                log_loginattempt(False, userDB.email)
        else:
            # Generisk feilmelding dersom noe går galt
            flash('Something went wrong. Please try again.')
            log_loginattempt(False, userDB.email)

    # dersom noe gaar galt rendre samme side
    return render_template("login.html", form=form), disable_caching


# If we need a method for a user to log out :
@app.route("/logout")
@login_required
def logout():
    #slett ifra redis først ellers er current_user ikke definert.
    redis.delete(current_user.email)
    log_logout(current_user.email)

    #Logg så ut fra login manager
    logout_user()
    return redirect(url_for('home')), disable_caching
