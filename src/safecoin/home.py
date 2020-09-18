from flask import render_template, url_for, redirect, request, flash
from flask_login import login_user, current_user, logout_user
### ------ Internal imports below ------ ###
from safecoin import app, db, bcrypt
from safecoin.models import User
from safecoin.forms import LoginForm
from safecoin.overview import overviewPage


# --- Main page --- #
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def home():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(overviewPage)
        else:
            flash('Wrong username or password. Please try again.')
    return render_template("login.html", form=form)

# If we need a method for a user to log out:
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


#app.route('/overview')
#ef helloOverview():
#   return 'Hello from overview'

