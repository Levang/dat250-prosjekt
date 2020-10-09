from flask import render_template, redirect, url_for, flash, get_flashed_messages
from flask_login import login_required
from safecoin import app
from safecoin.forms import PayForm, ValidatePaymentForm, flash_all_but_field_required
from safecoin.overview import overviewPage
from time import sleep


@app.route('/pay/', methods=["GET", "POST"])
#@login_required
def payPage():

    form = PayForm()
    form.get_select_field(None)
    form_validate = ValidatePaymentForm()

    # Pressed proceed button on validation page
    if form_validate.is_submitted() and form_validate.email_payment.data and form_validate.password_payment.data:
        # TODO Check if form_validate form contains the right email and password (and google auth?)
        # TODO If authenticated: Proceed transaction and return to overview page with a confirmation message
        flash(f"Successfully transferred {form_validate.kr.data},{form_validate.ore.data if form_validate.ore.data else '00'},- from account {form.tfrom.data} to {form.to.data}!", "success")
        sleep(1.5)  # Makes it look like it's working on something. I do not intend to remove this!
        return render_template('pay.html', form=form)

    # Pressed pay on validation page, and required fields in form is filled
    # or form in validation page isn't filled
    if form.validate_on_submit():
        return render_template("validate_payment.html", form=form_validate)

    # Regular pay page
    return render_template('pay.html', form=form)
