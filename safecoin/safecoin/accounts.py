from flask import render_template, request, flash, redirect
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from safecoin.accounts_db import addNewAccountToUser
from safecoin import app
from safecoin.forms import AccountsForm, flash_all_but_field_required, CreateAccountForm, CreateDeleteForm
from safecoin.tmp import account_list


@app.route("/accounts/", methods=["GET", "POST"])
@login_required
def accounts():
    form = AccountsForm()
    form.get_select_field(None)

    create_form = CreateAccountForm()
    delete_form = CreateDeleteForm()

    # Change this when we can get list of accounts
    global account_list
    # current_user.username

    do_action = True if form.create_account.data or form.delete_account.data else False
    create_form_start = True if form.create_account.data and form.account_name.data else False
    delete_form_start = True if form.delete_account.data and form.account_select.data else False

    if create_form.validate_on_submit():
        flash(f"Successfully Created Account {create_form.account_name.data}!", "success")

    if delete_form.validate_on_submit():
        flash(f"Successfully Deleted Account {delete_form.account_select.data}!", "success")

    if do_action:
        if form.create_account.data:
            if create_form_start:
                return render_template('validate_create_account.html', form=create_form)
            flash("Please enter a nickname for your account", "error")
            return render_template('accounts.html', account_list=account_list, form=form)
        if delete_form_start:
            return render_template('validate_delete_account.html', form=delete_form)

    return render_template('accounts.html', account_list=account_list, form=form)
