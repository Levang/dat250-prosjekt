from flask import render_template, redirect, url_for, flash, get_flashed_messages
from flask_login import login_required
from time import sleep
from safecoin import app
from safecoin.forms import PayForm, ValidatePaymentForm, flash_all_but_field_required
from safecoin.overview import overviewPage
from safecoin.accounts import getAccountsList
from safecoin.accounts_db import format_account_number


def intconvert_if_possible(var):
    try:
        return int(var)
    except ValueError:
        return var


def get_form_errors(from_, to, msg, kr, ore):
    myaccounts = getAccountsList()
    errlist = []
    general_error = False  # For returning a non informative error #PLEASE USE raise Exception("")

    try:
        # Verifies that from_ is in current users account
        if from_ == 'x':
            errlist.append("Please select an account to transfer from")
        else:
            from_ = intconvert_if_possible(from_)
            from_in_myaccounts = False
            for account in myaccounts:
                if account[1] == from_:
                    from_in_myaccounts = True
                    break
            if not from_in_myaccounts:
                general_error = True

        to = intconvert_if_possible(to)

        # Verifies that from_ and to isn't the same account
        if from_ == to:
            errlist.append("Can't transfer to the same account you transfer from")

        # Verify account number in to
        if type(to) != int or len(str(to)) != 11:
            # TODO Verify that the account number in "to" is a valid account number
            errlist.append("The account you want to pay to is invalid")

        kr = intconvert_if_possible(kr)
        ore = intconvert_if_possible(ore) if ore else 0

        if type(kr) != int or type(ore) != int or len(str(ore)) > 2 or float(f"{kr}.{ore}") <= 0:
            errlist.append("Please enter a valid amount to transfer")

        if not msg and (type(msg) != str or len(msg) > 256):
            errlist.append("KID/message is too long")
    except:
        general_error = True

    if general_error:
        errlist.append("An error occured")

    return errlist


@app.route('/pay/', methods=["GET", "POST"])
# @login_required
def payPage():
    account_list = getAccountsList()

    form = PayForm()
    form.get_select_field(account_list)
    form_validate = ValidatePaymentForm()

    # Pressed proceed button on validation page
    if form_validate.is_submitted() and form_validate.email_payment.data and form_validate.password_payment.data:
        errlist = get_form_errors(form_validate.tfrom.data, form_validate.to.data, form_validate.msg.data, form_validate.kr.data, form_validate.ore.data)
        # TODO Check if form_validate form contains the right email and password (and google auth?)
        # TODO If authenticated: Proceed transaction and return to overview page with a confirmation message
        # TODO Else: return pay.html with error (see if errlist below)
        if errlist:
            flash("An error occurred during validation. Didn't transfer anything.")
            return render_template('pay.html', form=form)
        flash(
            f"Successfully transferred {form_validate.kr.data},{form_validate.ore.data if form_validate.ore.data else '00'} kr from account {format_account_number(form.tfrom.data)} to {format_account_number(form.to.data)}!",
            "success")
        sleep(1.5)  # Makes it look like it's working on something. I do not intend to remove this!
        return render_template('pay.html', form=form)

    # Pressed pay on validation page, and required fields in form is filled
    # or form in validation page isn't filled
    if form.validate_on_submit():
        errlist = get_form_errors(form.tfrom.data, form.to.data, form.msg.data, form.kr.data, form.ore.data)
        if errlist:
            for err in errlist:
                flash(err, "error")
            return render_template('pay.html', form=form)
        return render_template("validate_payment.html", form=form_validate)

    # Regular pay page
    return render_template('pay.html', form=form)
