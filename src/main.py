from flask import Flask, render_template, request, flash, get_flashed_messages, redirect

from pages.register import registerUser
from pages.database import SqlDb

app = Flask(__name__)
app.secret_key = "i am a potato"
db = SqlDb()
db.create_users_table()


# --- Main page --- #
@app.route("/")
def home():
    return render_template("index.html")


# --- Register page --- #
@app.route("/register/")
def register():
    return render_template("register.html")


@app.route("/register/", methods=["POST"])
def process_registration():
    try:
        errs = registerUser(request.form["mail"], request.form["password"], request.form["repass"])
    except KeyError:
        errs = None
    if errs:
        for err in errs:
            flash(f"{err}", "error")
        return redirect("/register/")
    db.add_user(request.form["mail"], request.form["password"])
    return "Registered!"


if __name__ == '__main__':
    app.run(debug=True)
