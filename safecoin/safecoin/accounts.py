from flask import render_template, request, flash
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from safecoin.accounts_db import addNewAccountToUser
from safecoin import app
from safecoin.forms import AccountsForm, ValidateForm, flash_all_but_field_required
from safecoin.tmp import account_list


def pressed_create_account():
    pass


def pressed_delete_account(nr):
    pass


@app.route("/accounts/", methods=["GET", "POST"])
# @login_required
def accounts():
    form = AccountsForm()
    form.get_select_field(None)

    form_validate = ValidateForm()

    #

    # Change this when we can get list of accounts
    global account_list
    # current_user.username

    if form.validate_on_submit() or form_validate.is_submitted():
        if form_validate.is_submitted():
            # Run if submit button on auth page is pressed
            if form_validate.validate():
                # Run if valid info in auth form
                # TODO: Verify that auth is correct
                if form.create_account.data:
                    pressed_create_account()
                elif form.delete_account.data:
                    pressed_delete_account(form.account_select.data)
            else:
                # Run if form is incorrectly filled (aka not email in email field)
                flash_all_but_field_required(form_validate.email)
        return render_template("validate_request.html", form=form_validate)
    return render_template('accounts.html', account_list=account_list, form=form)
