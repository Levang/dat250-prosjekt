from flask import render_template, redirect, url_for, flash, get_flashed_messages
from flask_login import login_required
from safecoin import app
from safecoin.forms import PayForm, ValidateForm, flash_all_but_field_required
from safecoin.overview import overviewPage
from time import sleep


@app.route('/pay', methods=["GET", "POST"])
@login_required
def payPage():
    form = PayForm()
    form.get_select_field(None)
    form_validate = ValidateForm()

    # Pressed proceed button on validation page
    if form_validate.validate_on_submit():
        # TODO Check if form_validate form contains the right email and password (and google auth?)
        # TODO If authenticated: Proceed transaction and return to overview page with a confirmation message
        sleep(2)  # Makes it look like it's working. I do not intend to remove this!
        return redirect("/overview/")

    # Pressed pay on validation page, and required fields in form is filled
    # or form in validation page isn't filled
    if form.validate_on_submit() or form_validate.is_submitted():
        if form_validate.validate():
            flash_all_but_field_required(form_validate.email)
        return render_template("validate_request.html", form=form_validate)

    # Regular pay page
    return render_template('pay.html', form=form)
