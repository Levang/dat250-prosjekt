from flask import render_template, redirect, url_for
from flask_login import login_required
from safecoin import app
from safecoin.forms import PayForm
from safecoin.validate_request import validate


@app.route('/pay', methods=["GET", "POST"])
# @login_required
def payPage():
    form = PayForm()
    form.get_select_field(None)
    if form.validate_on_submit():
        return validate()
    return render_template('pay.html', form=form)
