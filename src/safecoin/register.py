from flask import render_template, url_for, redirect, request, flash
###################
from safecoin import app, db
from safecoin.models import User
from safecoin.forms import RegistrationForm, LoginForm


def saveInDatabase():
    pass


def getPasswordViolations(errList, password):
    if type(password) != str:
        return "An error occured!"

    # Password params
    want_length = 8
    want_numbers = 3

    if len(password) < want_length:
        errList.append(f"Password should be at least {want_length} characters")

    numbers = 0
    for letter in password:
        try:
            int(letter)
            numbers += 1
        except ValueError:
            pass

    if numbers < want_numbers:
        errList.append(f"Password must have at least {want_numbers} numbers from 0-9")


def registerUser(email, password, repass):
    errList = []
    if password != repass:
        errList.append("Passwords doesn't match")
        return errList
    if not getPasswordViolations(errList, password):
        return errList
    return None


# --- Register page --- #
#@app.route("/register/")
#def register():
#    return render_template("register.html")


@app.route("/register/", methods=["GET", "POST"])
def process_registration():
    # try:
    #    errs = registerUser(request.form["mail"], request.form["password"], request.form["repass"])
    # except KeyError:
    #    errs = None
    #if errs:
    #    for err in errs:
    #        flash(f"{err}", "error")
    #    return redirect("/register/")
    ## db.add_user(request.form["email"], request.form["password"])
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return "OK"
    return render_template("register.html", form=form)
    #form.email()
    #user = User(email=request.form["email"], password=request.form["password"])
    #db.session.add(user)
    #db.session.commit()
    #return "Registered!"
