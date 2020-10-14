
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


@app.route("/transactions/", methods=["GET", "POST"])
@login_required
def transactions():
    return render_template('hist_transfer.html')

