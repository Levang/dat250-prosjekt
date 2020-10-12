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


# ─── CREATES AND ADDS TO ACCOUNTS DATABASE ──────────────────────────────────────
# ─── FOR TESTING FORMATTING AND DEVELOPING ──────────────────────────────────────
def createTestingAcc():
    listAccounts=[None]*30
    for i in range(30):
        temp=Account(number=random.randint(11112200000,11112299999), balance=random.randint(0,10000),pub_key=random.randint(0,1000000000000))
        db.session.add(temp)

    db.session.commit()

