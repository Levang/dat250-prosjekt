from flask import render_template, flash
from flask_login import login_required, current_user

from safecoin import app, disable_caching
from safecoin.forms import PayForm, ValidatePaymentForm
from safecoin.encryption import getAccountsList, submitTransaction
from safecoin.accounts_db import format_account_number, illegalChar
from safecoin.models import Account
from safecoin.logging import log_transfer


def intconvert_if_possible(var):
    try:
        return int(var)
    except ValueError:
        return var


def krToInt(kr, ore):
    if ore == None:
        ore = 0
    # Kr og ore maa kunne konverteres til int, dersom det feiler. er det en feil
    try:
        kr = int(kr)
        kr = str(kr)

        ore = int(ore)
        # Kan ikke ha mer enn 99 ore eller mindre enn null
        if ore > 99 or ore < 0:
            return None
        elif ore < 10:
            ore = f"0{ore}"
        else:
            ore = str(ore)
    except:
        return None

    amount = kr + ore
    return int(amount)


def get_form_errors(accountFrom, accountTo, kr, ore, msg):
    myaccounts = getAccountsList()
    errlist = []
    general_error = False  # For returning a non informative error #PLEASE USE raise Exception("")

    amount = krToInt(kr, ore)
    if not amount:
        errlist.append("Please enter a valid amount to transfer")

    # Verifies that from_ is in current users account, yes on redis...
    if accountFrom == 'x':
        errlist.append("Please select an account to transfer from")

    else:
        accountFrom = intconvert_if_possible(accountFrom)
        from_in_myaccounts = False
        for account in myaccounts:
            if account[1] == accountFrom:
                from_in_myaccounts = True
                break
        if not from_in_myaccounts:
            errlist.append("An error occured")

    # Verifies that from_ and to isn't the same account
    if accountFrom == accountTo:
        errlist.append("Can't transfer to the same account you transfer from")

    if len(str(accountTo)) != 11:
        errlist.append("Invalid account number")

    accTo = Account.query.filter_by(number=accountTo).first()
    if not accTo:
        errlist.append(f"Unable to transfer to {accountTo}, it does not exist")

    if amount < 1:
        errlist.append("Please enter a valid amount to transfer")

    if illegalChar(msg, 256):
        errlist.append("Invalid KID/message or too long")

    if general_error:
        errlist.append("An error occured")

    return errlist


@app.route('/transfer/', methods=["GET", "POST"])
@login_required
def payPage():
    account_list = getAccountsList()

    form = PayForm()
    form.get_select_field(account_list)
    form_validate = ValidatePaymentForm()

    # Pressed proceed button on validation page
    if form_validate.is_submitted() and form_validate.password_payment.data:
        errlist = get_form_errors(form_validate.tfrom.data, form_validate.to.data, form_validate.kr.data, form_validate.ore.data, form_validate.msg.data)
        if errlist:
            try:
                log_transfer(is_validated=False,
                             from_=form_validate.tfrom.data,
                             to=form_validate.to.data,
                             kid=form_validate.msg.data,
                             amount=krToInt(kr=form_validate.kr.data, ore=form_validate.ore.data),
                             hashedEmail=current_user.email,
                             custommsg="TransactionError")
            except:
                log_transfer(is_validated=False, hashedEmail=current_user.email, custommsg="TransactionError")
            flash("An error occurred during validation. Didn't transfer anything.")
            return render_template('pay.html', form=form), disable_caching

        transaction_ok = submitTransaction(
            password = form_validate.password_payment.data,
            accountFrom = form_validate.tfrom.data,
            accountTo = form_validate.to.data,
            amount = krToInt( kr = form_validate.kr.data , ore = form_validate.ore.data ),
            message =form_validate.msg.data
            )

        if not transaction_ok:
            try:
                log_transfer(is_validated=False,
                             from_=form_validate.tfrom.data,
                             to=form_validate.to.data,
                             kid=form_validate.msg.data,
                             amount=krToInt(kr=form_validate.kr.data, ore=form_validate.ore.data),
                             hashedEmail=current_user.email,
                             custommsg="TransactionError")
            except:
                log_transfer(is_validated=False, hashedEmail=current_user.email, custommsg="TransactionError")
            flash("An error occurred during validation. Didn't transfer anything.")
        else:
            log_transfer(is_validated=True,
                         from_=form_validate.tfrom.data,
                         to=form_validate.to.data,
                         kid=form_validate.msg.data,
                         amount=krToInt(kr=form_validate.kr.data, ore=form_validate.ore.data),
                         hashedEmail=current_user.email)
            flash(
                f"Successfully transferred {form_validate.kr.data},{form_validate.ore.data if form_validate.ore.data else '00'} kr from account {format_account_number(form.tfrom.data)} to {format_account_number(form.to.data)}!",
                "success")
        # sleep(1.5)  # Makes it look like it's working on something. I do not intend to remove this!
        return render_template('pay.html', form=form), disable_caching

    # Pressed pay on validation page, and required fields in form is filled
    # or form in validation page isn't filled
    if form.validate_on_submit():
        errlist = get_form_errors(form.tfrom.data, form.to.data, form.kr.data, form.ore.data, form.msg.data)
        if errlist:
            for err in errlist:
                flash(err, "An error occurred")
            return render_template('pay.html', form=form), disable_caching

        return render_template("validate_payment.html", form=form_validate), disable_caching
    # Regular pay page
    return render_template('pay.html', form=form), disable_caching
