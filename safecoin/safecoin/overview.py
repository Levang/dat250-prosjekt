
from safecoin.accounts import format_account_list, format_account_number

import random

from flask import render_template, request, flash, redirect
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from safecoin.accounts_db import addNewAccountToUser

from safecoin import app, redis, json, db
from safecoin.forms import AccountsForm, flash_all_but_field_required, CreateAccountForm, CreateDeleteForm
from safecoin.tmp import TmpAcc
from safecoin.models import Account, User
from safecoin.accounts_db import format_account_number


@app.route("/overview/", methods=["GET", "POST"])
@login_required
def overviewPage():
    account_list = getAccountsList()

    form = AccountsForm()
    form.get_select_field(account_list)
    format_account_list(account_list)

    create_form = CreateAccountForm()
    delete_form = CreateDeleteForm()

    do_action = True if form.create_account.data or form.delete_account.data else False
    create_form_start = True if form.create_account.data and form.account_name.data else False
    delete_form_start = True if form.delete_account.data and form.account_select.data else False

    if create_form.validate_on_submit():
        flash(f"Successfully Created Account {create_form.account_name.data}!", "success")

    if delete_form.validate_on_submit():
        flash(f"Successfully Deleted Account {delete_form.account_select.data}!", "success")

    if do_action:
        if form.create_account.data:
            if create_form_start:
                return render_template('validate_create_account.html', form=create_form)
            flash("Please enter a nickname for your account", "error")
            return render_template('overview.html', account_list=account_list, form=form)
        if delete_form_start:
            if form.account_select.data == 'x':
                flash("Please select an account", "error")
                return render_template('overview.html', account_list=account_list, form=form)
            return render_template('validate_delete_account.html', form=delete_form)

    return render_template('overview.html', account_list=account_list, form=form)


def getAccountsList():
    userDict = redis.get(current_user.email)
    userDict = json.loads(userDict)

    i = 0
    account_list = []
    for accountnr in userDict['accounts']:  # Denne fungerer men må ryddes opp i, gjør det om til en funksjon elns.
        numberUsr = int(accountnr)
        name = userDict['accounts'][accountnr][0]  # noe galt her no time to fix atm. Fikser senere

        accountDB = Account.query.filter_by(number=numberUsr).first()
        if accountDB:
            balance = round(accountDB.balance, 2)
            # print(name)
            account_list.append([name, numberUsr, balance])
        else:
            return None

        i += 1
    return account_list



#@app.route('/transactions/')
#@login_required
#def histPage():
    #return render_template('hist_transfer.html')


#@app.route('/transfer/')
#@login_required
#def transferPage():
    #return render_template('transfer.html')


#@app.route('/profile/')
#@login_required
#def profilePage():

    #createTestingAcc() #creates testing accounts that are added to accounts database

    #return render_template('profile.html')


# ─── CREATES AND ADDS TO ACCOUNTS DATABASE ──────────────────────────────────────
# ─── FOR TESTING FORMATTING AND DEVELOPING ──────────────────────────────────────
def createTestingAcc():
    listAccounts=[None]*30
    for i in range(30):
        temp=Account(number=random.randint(11112200000,11112299999), balance=random.randint(0,10000),pub_key=random.randint(0,1000000000000))
        db.session.add(temp)

    db.session.commit()

