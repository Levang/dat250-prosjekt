# ─── NOTATER ARDIJAN ────────────────────────────────────────────────────────────
# ─── FIKS ───────────────────────────────────────────────────────────────────────
# Overview          --DONE
# Ny account        --Doing
# Pay funksjon      --
# Slett account     --
# Trans historikk   --
# ─── NOTATER ARDIJAN ────────────────────────────────────────────────────────────

from safecoin.accounts import format_account_list, format_account_number

import random

from flask import render_template, request, flash, redirect
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from safecoin.accounts_db import addNewAccountToCurUser

from safecoin import app, redis, json, db
from safecoin.forms import AccountsForm, flash_all_but_field_required, CreateAccountForm, CreateDeleteForm
from safecoin.tmp import TmpAcc
from safecoin.models import Account, User
from safecoin.accounts_db import format_account_number


@app.route("/overview/", methods=["GET", "POST"])
@login_required
def overviewPage():
    account_list = getAccountsList()
    print(account_list)
    form = AccountsForm()
    #form.get_select_field(account_list)
    format_account_list(account_list)

    if account_list==None:
        account_list=[['','Please open an account','']]

    elif len(account_list)>5:
        account_list=account_list[:5]

    return render_template('overview.html', account_list=account_list, form=form)


def getAccountsList():
    if current_user.accounts==None:
        return [['','Please open an account','']]

    print("ACCOUNTS LIST PRINTING")
    print(current_user.accounts)
    print("ACCOUNTS LIST PRINTING")

    userDict = redis.get(current_user.email)
    userDict = json.loads(userDict)

    i = 0
    account_list = []

    #SJEKK OM ME FUCKER UP!

    # Denne fungerer men må ryddes opp i, gjør det om til en funksjon elns.
    for accountnr in userDict['accounts']:
        numberUsr = int(accountnr)

        #Navnet ligger i 0te index [navn,kontonr,secret]
        name = userDict['accounts'][accountnr][0]

        #Hent kontobalanse fra accounts database
        accountDB = Account.query.filter_by(number=numberUsr).first()

        if accountDB:
            balance = round(accountDB.balance, 2)
            # print(name)
            account_list.append([name, numberUsr, balance])
        else:
            return None

        i += 1
    return account_list





# ─── CREATES AND ADDS TO ACCOUNTS DATABASE ──────────────────────────────────────
# ─── FOR TESTING FORMATTING AND DEVELOPING ──────────────────────────────────────
def createTestingAcc():
    listAccounts=[None]*30
    for i in range(30):
        temp=Account(number=random.randint(11112200000,11112299999), balance=random.randint(0,10000),pub_key=random.randint(0,1000000000000))
        db.session.add(temp)

    db.session.commit()

