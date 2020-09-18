from flask import render_template, url_for, redirect
from safecoin import app


@app.route('/overview')
def overviewPage():
    return render_template('overview.html')


@app.route('/transactions')
def histPage():
    return render_template('hist_transfer.html')


@app.route('/accounts')
def accountsPage():
    return render_template('accounts.html')


@app.route('/transfer')
def transferPage():
    return render_template('transfer.html')


@app.route('/pay')
def payPage():
    return render_template('pay.html')


@app.route('/profile')
def profilePage():
    return render_template('profile.html')
