from flask import render_template
from safecoin import app


# --- Main page --- #
@app.route("/")
def home():
    return render_template("index.html")


#app.route('/overview')
#ef helloOverview():
#   return 'Hello from overview'

