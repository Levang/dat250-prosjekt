
from safecoin.accounts import format_account_list, format_account_number

import random

from flask import render_template, request, flash, redirect
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from safecoin.accounts_db import addNewAccountToCurUser

from safecoin import app, redis, json, db, disable_caching
from safecoin.forms import AccountsForm, flash_all_but_field_required, CreateAccountForm, CreateDeleteForm
from safecoin.tmp import TmpAcc
from safecoin.models import Account, User, Transactions
from safecoin.accounts_db import format_account_number


@app.route("/transactions/", methods=["GET", "POST"])
@login_required
def transactions():
    #eier jeg denne kontoen
    #sjekk redis
    #om ja, vis alle transactioner
    #user = User.query.filter((User.email == email) | (User.name == name)).first()
    selectedAccount="42856937499"
    kontoliste=[]
    #translist=db.query.filter_by(accountFrom=selectedAccount).all()
    transList=Transactions.query.filter((Transactions.accountFrom == selectedAccount) | (Transactions.accountTo == selectedAccount))
    print("HALLO")
    #order_by(Transactions.time)
    #print(transList.all().all())
    for i in transList:
        a=i.accountTo
        b=i.accountFrom
        print(a)
        print(b)

    return render_template('hist_transfer.html'), disable_caching

#Make function to retrive information from transactions database