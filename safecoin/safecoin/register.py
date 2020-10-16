from flask import render_template, url_for, redirect, request, flash
from configparser import ConfigParser
import base64
import pyotp
import flask_qrcode
###################
from safecoin import app, db, bcrypt
import flask_scrypt
from safecoin.encryption import encrypt, decrypt
from safecoin.models import User
from safecoin.forms import RegistrationForm, TwoFactorAuthRegForm
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
    form2 = TwoFactorAuthRegForm()
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

            #print(f"encryption key: {enKey}")
            # ─── TESTACCOUNTS ───────────────────────────────────────────────────────────────
            # ─── ADDS ACCOUNTS TO NEW USER REPLACED WHEN CREATE ACCOUT IS WORKING ───────────
            accountlist=[11112248371,11112239950,11112235147,11112205956,11112262143,11112270258,11112294379,11112250314,11112293269,11112278435,11112208700]
            accountName=['bob','Alot','savings','expences','toiletMoney','company1','company2','wifey','daughter','son','grandchild','brother','theTeapot','Games','gambling']
            # ─── TESTACCOUNTS ───────────────────────────────────────────────────────────────

            encryptedKey=encrypt(form.password.data,'generate',True) # generate new encrypted key with users password
            deKey=decrypt(form.password.data,encryptedKey,True)      # decrypt the key
            mailEncrypted=encrypt(deKey,form.email.data)             # encrypt the email

            # ─── TESTING ACCOUNTS ───────────────────────────────────────────────────────────
            # ─── ADDS ACCOUNTS TO NEW USER REPLACED WHEN CREATE ACCOUT IS WORKING ───────────
            accountsString=''
            for i in range(len(accountlist)):
                accountsString=accountsString + (f'{accountName[i]},{accountlist[i]},privatekey{i};')
            # ─── TESTING ACCOUNTS ───────────────────────────────────────────────────────────

            accountsEnc=encrypt(deKey,accountsString)

            print(f' decrytion key {deKey}')
            print(f' decryted email {decrypt(deKey,mailEncrypted)}')

            # ─── TESTING 2-FACTOR AUTHENTICATION ───────────────────────────────────────────────────#


            secret_key = pyotp.random_base32()  #Lager en relativt simpel secret_key, men det virker.
            qr_link = pyotp.totp.TOTP("A6OHFL6WPYGBARUV").provisioning_uri(name=form.email.data, issuer_name="Safecoin.tech") #Lager en OTP link som kan brukes til å generere QR-kode
            return render_template('2fak.html', form2 = form2, qr_link = qr_link) # Vi må dra med inn qr_linken for å generere qr_koden korrekt
        
        for err in errList:
            flash(err, "error")

            
    if form2.validate_on_submit():
            print("test")
            ## Må kanskje trekke med informasjon via redis inn her? email, enEmail, password of enKey potensielt?
            totp = pyotp.totp.TOTP("A6OHFL6WPYGBARUV")
            if totp.verify(form2.otp.data): # Hvis brukeren scanner qrkoden (som genereres i html) vil koden som vises i appen deres matche koden til totp.now()
                print("Iffen validerte!!")
                print(f"  -  {form2.email.data} _ {form.password.data}")
                user = User(email=hashed_email.decode("utf-8"), enEmail=mailEncrypted, password=(hashed_pw+salt).decode("utf-8"),enKey=encryptedKey, secret=secret_key)             #------------ Legger til secret key i database-brukeren -----------------#
                user.accounts=accountsEnc
                db.session.add(user)
                db.session.commit()
                flash('Your account has been created! You are now able to log in.', 'success')

                return redirect(url_for('home'))
    return render_template("register.html", form=form)