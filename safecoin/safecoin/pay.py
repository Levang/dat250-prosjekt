from flask import render_template
from flask_login import login_required
from safecoin import app


@app.route('/pay')
# @login_required
def payPage():
    return render_template('pay.html')
