from flask import render_template, url_for, redirect
from flask_login import login_required, current_user
from safecoin import app, redis, json, db
from safecoin.models import Account, User

import random

@app.route('/overview/')
@login_required
def overviewPage():
    return render_template('overview.html')


@app.route('/transactions/')
@login_required
def histPage():
    return render_template('hist_transfer.html')


@app.route('/transfer/')
@login_required
def transferPage():
    return render_template('transfer.html')


@app.route('/profile/')
@login_required
def profilePage():

    #createTestingAcc() #creates testing accounts that are added to accounts database

    return render_template('profile.html')



def createTestingAcc():
    listAccounts=[None]*30
    for i in range(30):
        temp=Account(number=random.randint(11112200000,11112299999), balance=random.randint(0,10000),pub_key=random.randint(0,1000000000000))
        db.session.add(temp)
        # print(listAccounts[i].balance)


    db.session.commit()


# encryptedKey=encrypt(form.password.data,'generate',True) # generate new encrypted key with users password
# deKey=decrypt(form.password.data,encryptedKey,True)      # decrypt the key
# mailEncrypted=encrypt(deKey,form.email.data)             # encrypt the email
# accountsEnc=encrypt(deKey,testvalue)

# print(f' decrytion key {deKey}')
# print(f' decryted email {decrypt(deKey,mailEncrypted)}')

# user = User(email=hashed_email.decode("utf-8"), enEmail=mailEncrypted, password=(hashed_pw+salt).decode("utf-8"),enKey=encryptedKey)
# user.accounts=accountsEnc
# db.session.add(user)
# db.session.commit()


# class Account(db.Model):
#     number = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
#     balance = db.Column(db.Numeric(256)) #tallet viser til maks lengde av et siffer
#     pub_key = db.Column(db.String(300), unique=True, nullable=False)
