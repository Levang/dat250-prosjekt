from flask import render_template, url_for, redirect
from safecoin import app
@app.route('/overview')
def helloOverview():
    return render_template('overview.html')
