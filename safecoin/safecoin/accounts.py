from flask import render_template, request, flash
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from safecoin.accounts_db import addNewAccountToUser
from safecoin import app


# Temporary...
class TmpAcc:
    def __init__(self, nr, balance):
        self.number = nr
        self.balance = balance

    def delete(self):
        pass


account_list = [TmpAcc(1, 2000), TmpAcc(2, 0), TmpAcc(43, 50), TmpAcc(54, 2000), TmpAcc(7, 0), TmpAcc(12, 50)]


@login_required
@app.route("/accounts/", methods=["GET", "POST"])
def accounts():
    clicked_acc = None
    # Change this when we can get list of accounts
    global account_list
    # current_user.username
    if request.method == "POST":
        flash("Account deleted!", "success")
    return render_template('accounts.html', account_list=account_list)
