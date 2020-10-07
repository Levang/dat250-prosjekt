from flask import render_template
from flask_login import login_required
from safecoin import app
from safecoin.forms import PayForm


@app.route('/pay')
# @login_required
def payPage():
    form = PayForm()
    if form.validate_on_submit():
        print(123)
        return render_template('/')
    return render_template('pay.html', form=form)
