from flask import render_template
from safecoin import app


# --- Main page --- #
@app.route("/")
def homePage():
    return render_template("index.html")

@app.route("/login")
def loginPage():
    return render_template("login.html")
#app.route('/overview')
#ef helloOverview():
#   return 'Hello from overview'

