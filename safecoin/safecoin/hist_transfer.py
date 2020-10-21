
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

    fromTrans = TransHistory
    formTrans.
    #TODO make this get info from dropdown.
    selectedAccount="41656916900"

    userDict=getAccountsList()

    for i in userDict['accounts']:
        accounts['accounts'][i]

    if selectedAccount not in userDict['accounts']:
        #Account does not belong to user

        return


    transHistory=Transactions.query.filter((Transactions.accountFrom == selectedAccount) | (Transactions.accountTo == selectedAccount))

    #TODO jinja cant format time object, need to convert to localtime anyways. 
    #Just make new class and add every field so we can format all thje stuff

    return render_template('hist_transfer.html', transHistory=transHistory), disable_caching

#Make function to retrive information from transactions database