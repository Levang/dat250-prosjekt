
from safecoin.accounts import format_account_list, format_account_number

import random

from flask import render_template, request, flash, redirect
from flask_login import current_user, login_required
from flask_wtf import FlaskForm

from safecoin import app, redis, json, db, disable_caching
from safecoin.forms import AccountsForm
from safecoin.models import Transactions
from safecoin.accounts_db import format_account_number
from safecoin.accounts import getAccountsList


@app.route("/transactions/", methods=["GET", "POST"])
@login_required
def transactions():
    #eier jeg denne kontoen
    #sjekk redis 41656916900 
    #om ja, vis alle transactioner
    #user = User.query.filter((User.email == email) | (User.name == name)).first()
    #TODO make this a dropdown.
    selectedAccount="41656916900"

    userDict=json.loads(redis.get(current_user.email))

    if selectedAccount not in userDict['accounts']:
        #Account does not belong to user
        print('SHITFACE')
        return

   #transHistory = []
    #translist=db.query.filter_by(accountFrom=selectedAccount).all()
    transHistory=Transactions.query.filter((Transactions.accountFrom == selectedAccount) | (Transactions.accountTo == selectedAccount))
    print("HALLO")
    #order_by(Transactions.time)
    #print(transList.all().all())
    # for i in transList: 
    #     #print(f"from:{i.accountFrom} to: {i.accountTo}, amount : {i.amount}, Time of Transaction: {i.time}")
    #     liste=[str(i.accountFrom), str(i.accountTo),str(i.amount),str(i.time)]
    #     print(liste)

    #TODO jinja cant format time object, need to convert to localtime anyways. 
    #Just make new class and add every field so we can format all thje stuff

    return render_template('hist_transfer.html', transHistory=transHistory), disable_caching

#Make function to retrive information from transactions database