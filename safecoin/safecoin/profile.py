from flask import render_template
from flask_login import login_required
from safecoin import app


@app.route('/profile/')
@login_required
def profilePage():
    return render_template('profile.html')
