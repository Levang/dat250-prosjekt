from flask import render_template
from flask_login import login_required, fresh_login_required

from safecoin import app, disable_caching
from safecoin.forms import AccountsForm
from safecoin.encryption import getAccountsList, getCurUsersEmail
from safecoin.accounts import format_account_list


@app.route("/overview/", methods=["GET", "POST"])
@login_required
@fresh_login_required
def overviewPage():
    account_list = getAccountsList()
    form = AccountsForm()
    format_account_list(account_list)

    if account_list is None:
        account_list = [['', 'Please open an account', '']]

    elif len(account_list) > 5:
        account_list = account_list[:5]

    email = "HACKER"
    try:
        email = getCurUsersEmail().upper().split("@")[0]
    except:
        try:
            email = getCurUsersEmail().upper()
        except:
            pass

    return render_template('overview.html', account_list=account_list, form=form, email=email), disable_caching
