from flask import render_template, request, flash
from flask_login import current_user, login_required
from safecoin.accounts_db import addNewAccountToUser
from safecoin import app


@login_required
@app.route("/accounts/", methods=["GET", "POST"])
def accounts():
    account_list = []
    # current_user.username
    if request.method == "POST":
        flash("Account deleted!", "success")
    return render_template('accounts.html', account_list=account_list)
