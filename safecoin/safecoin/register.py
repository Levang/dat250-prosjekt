from flask import render_template, url_for, redirect, request, flash
from configparser import ConfigParser
import base64
import pyotp
import flask_qrcode
###################
from safecoin import app, db, bcrypt, redis, json, disable_caching
import flask_scrypt
from safecoin.encryption import encrypt, decrypt, dictToStr
from safecoin.models import User
from safecoin.forms import RegistrationForm, TwoFactorAuthRegForm
from safecoin.accounts_db import addNewAccountToCurUser
#from safecoin.accounts import addNewAccountToUser
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


@app.route("/register/", methods=["GET", "POST"])
def register():
    if RegistrationForm().email:
        carryOverEmail = RegistrationForm().email.data
    form = RegistrationForm()
    form2 = TwoFactorAuthRegForm()

    # form er den første formen som er på /register, som per nå bare inneholder email, passord og en submit-knapp

    # form2 er den andre formen du kommer til etter du submitter "form". Denne nye siden vil da inneholde QR-koden
    # for å legge 2fa-nøkkelen inn i din valgte 2fa app. Denne siden har også et passord felt, 2fa felt (for koden du nå kan generere i appen),
    # og et "read-only" som inneholder eposten du skrev inn på forrige side.
    if form.validate_on_submit():
        print("THIS RAN")

        errList = []
        getPasswordViolations(errList, form.password.data)

        # Is there any error in the generated information
        if len(errList) == 0:

            # ─── HASHED EMAIL IS USER ID ─────────────────────────────────────
            hashed_email = flask_scrypt.generate_password_hash(form.email.data, "")

            # Key MUST have register keyword appended so as not to mix user keys in redis server
            registerRedisKey = hashed_email + "register".encode('utf-8')

            # ─── CHECK IF THE EMAIL EXISTS IN DATABASE OR REDIS ───────────────────────
            if User.query.filter_by(email=hashed_email.decode("utf-8")).first() or redis.get(registerRedisKey):
                flash("error")
                return render_template("register.html", form=form), disable_caching

            # ─── IF THE USER DOES NOT EXIST IN THE DATABASE ──────────────────
            # Create a user dictionairy for redis.
            userDict = {}

            # add hashed email as key to cleartext email
            # This can be directly saved to database later as user email
            userDict['email'] = hashed_email.decode("utf-8")

            # We need to temporarily keep the users email in plaintext while in redis

            userDict["PlainEmail"] = form.email.data

            # ─── SALT AND HASH PASSWORD ──────────────────────────────────────
            salt = flask_scrypt.generate_random_salt()

            # add hashed password to user dictionairy
            # This can be directly saved to database later
            userDict['password'] = flask_scrypt.generate_password_hash(form.password.data, salt) + salt

            # ─── GENERATE USER ENCRYPTION KEY ────────────────────────────────

            # generate new encrypted key with users password
            encryptedKey = encrypt(form.password.data, 'generate', True)

            # decrypt the key again, serves as a double check
            deKey = decrypt(form.password.data, encryptedKey, True)

            # If deKey, explicitly show what you are testing this against none.
            if deKey != None:
                userDict['enKey'] = encryptedKey

            # encrypt the email and add it to userDict
            userDict['enEmail'] = encrypt(deKey, form.email.data)

            # ─── TESTING 2-FACTOR AUTHENTICATION ───────────────────────────────────────────────────#

            # Lager en relativt simpel secret_key. Har kompatibilitet med Google Authenticator.
            secret_key = pyotp.random_base32()

            # denne maa tas vare på til neste side, krypteres med kundes passord
            userDict['secret'] = encrypt(deKey, secret_key)

            # Genererer link for kundes qr kode
            qr_link = pyotp.totp.TOTP(secret_key).provisioning_uri(name=form.email.data, issuer_name="Safecoin.tech")

            # json generate string from dict overwrite the dict from before
            userDict = dictToStr(userDict)

            #Add it to the redis server
            redis.set(registerRedisKey,userDict)
            #Set session timeout of user at 600 secons, 10 minutes
            redis.expire(registerRedisKey,600)
            return render_template('TwoFactor.html', form2 = form2, qr_link = qr_link), disable_caching  # Vi må dra med inn qr_linken for å generere qr_koden korrekt


        # ─── DERSOM FEIL VED REGISTEREING ───────────────────────────────────────────────
        for err in errList:
            flash(err, "error")

    if form2.validate_on_submit():

            #Regenerate hashed email from last page
            hashed_email = flask_scrypt.generate_password_hash(carryOverEmail, "")

            #Key MUST have register keyword appended so as not to mix user keys in redis server
            registerRedisKey=hashed_email+"register".encode('utf-8')

            #retrive information from redis
            userDict=redis.get(registerRedisKey)

            #delete user from redis
            redis.delete(registerRedisKey)

            #Format back to dictionairy
            userDict = json.loads(userDict)

            #Check password correctness
            pwOK = flask_scrypt.check_password_hash(form2.password_2fa.data.encode('utf-8'), userDict['password'][:88].encode('utf-8'), userDict['password'][88:176].encode('utf-8'))
            print("ER PASSORD OK?")
            print(pwOK)
            if pwOK:
                #Decrypt the users decryption key
                decryptionKey=decrypt(form2.password_2fa.data.encode('utf-8'),userDict['enKey'].encode('utf-8'),True)

                #Decrypt 2FA key with user decryption key
                twoFAkey= decrypt(decryptionKey,userDict['secret'])

                #add key to the Timed One Timed Passwords class so it can verify
                totp = pyotp.totp.TOTP(twoFAkey)

                # Hvis brukeren scanner qrkoden (som genereres i html) vil koden som vises i appen deres matche koden til totp.now()
                if totp.verify(form2.otp.data):

                    print("LAGRER BRUKER I DATABASE")
                    #user = User(email=hashed_email.decode("utf-8"), enEmail=mailEncrypted, password=(hashed_pw+salt).decode("utf-8"),enKey=encryptedKey, secret=secret_key)

                    #Create user class
                    user = User()
                    user.email=hashed_email
                    user.enEmail=userDict['enEmail']
                    user.password=userDict['password']
                    user.enKey=userDict['enKey']
                    user.accounts=None
                    user.secret=userDict['secret']

                    db.session.add(user)
                    db.session.commit()
                    flash('Your account has been created! You are now able to log in.', 'success')

                    # ─── ADD ACCOUNT WITH MONEY TO USER ─────────────────────────────────────────────
                    #You start with an account that we add so that we and
                    #Whomever is going to thest our site can work with it
                    addNewAccountToCurUser(password=form2.password_2fa.data,user=User.query.filter_by(email=hashed_email).first(),money=True)
                    # ─── ADD ACCOUNT WITH MONEY TO USER ─────────────────────────────────────────────
                    return redirect(url_for('home'))
                else:
                    # Generisk feilmelding dersom noe går galt
                    flash('Something went wrong. Please try again.')

    return render_template("register.html", form=form), disable_caching
