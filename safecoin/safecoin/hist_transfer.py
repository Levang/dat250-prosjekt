
from safecoin.accounts import format_account_list, format_account_number

import random

from flask import render_template, request, flash, redirect
from flask_login import current_user, login_required
from flask_wtf import FlaskForm

from safecoin import app, redis, json, db, disable_caching
from safecoin.forms import TransHistory
from safecoin.models import Transactions
from safecoin.accounts_db import format_account_number
from safecoin.accounts import getAccountsList


@app.route("/transactions/", methods=["GET", "POST"])
@login_required
def transactions():

    transForm = TransHistory()
    #TODO make this get info from dropdown.
    #selectedAccount="41656916900"

    accountList=getAccountsList()
    transForm.get_select_field(accountList)

    transHistory=[]
    if transForm.view_hist.data and transForm.accountSelect.data!="x":
        print(accountList)
        if transForm.accountSelect.data in accountList:
            transHistory=Transactions.query.filter((Transactions.accountFrom == transForm.accountSelect.data) | (Transactions.accountTo == transForm.accountSelect.data))
        for i in transHistory:
            print(i.accountFrom)



    #print(transForm.account_select.data)

    #TODO jinja cant format time object, need to convert to localtime anyways.
    #Just make new class and add every field so we can format all thje stuff
    #form=transForm

    return render_template('hist_transfer.html', transHistory=transHistory, form=transForm), disable_caching