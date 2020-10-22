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

from safecoin import app, redis, json, db, disable_caching
from safecoin.forms import AccountsForm, flash_all_but_field_required, CreateAccountForm, CreateDeleteForm
from safecoin.models import Account, User
from safecoin.accounts_db import format_account_number
from safecoin.encryption import getAccountsList


@app.route("/overview/", methods=["GET", "POST"])
@login_required
def overviewPage():
    account_list = getAccountsList()
    print(account_list)
    form = AccountsForm()
    format_account_list(account_list)

    if account_list is None:
        account_list = [['', 'Please open an account', '']]

    elif len(account_list) > 5:
        account_list = account_list[:5]

    return render_template('overview.html', account_list=account_list, form=form), disable_caching
