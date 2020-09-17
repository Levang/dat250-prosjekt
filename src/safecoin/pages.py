from flask import render_template
#######################
from safecoin import app, db
from safecoin.forms import RegistrationForm, LoginForm
from safecoin.models import User


# --- Main page --- #
@app.route("/", methods=["GET", "POST"])
def home():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return "OK"
    return render_template("index.html", form=form)
