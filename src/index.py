# import sys
# sys.path.insert(0, '/pages')    #Dersom import ikke fungerer fjern kommentar
# ─── Linjene over tillater import som vanlig fra pages mappen ────────────────────────────────────────────────────────────────────────
from flask import Flask, render_template
from pages import overview 

app = Flask(__name__)

<<<<<<< HEAD
@app.route("/")
def login():
    return render_template("login.html")
=======

@app.route("/")
def home():
    return render_template("index.html")
>>>>>>> joachim

@app.route("/overview")
def overviewpage():
    return overview.hello_overview()


if __name__ == '__main__':
    app.run(debug=True)
