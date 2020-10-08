from flask import render_template, url_for, redirect
from flask_login import login_required, current_user
from safecoin import app, redis


@app.route('/overview/')
@login_required
def overviewPage():
    return render_template('overview.html')


@app.route('/transactions/')
@login_required
def histPage():
    return render_template('hist_transfer.html')


@app.route('/transfer/')
@login_required
def transferPage():
    return render_template('transfer.html')


@app.route('/profile/')
@login_required
def profilePage():
    # # for i in activeUsers:
    # #     print(i)
    # #     print(i.email)
    # # print(len(activeUsers))
    # print("finished")
    return render_template('profile.html',printmail=redis.get(current_user.email))
