# import sys
# sys.path.insert(0, '/pages')    #Dersom import ikke fungerer fjern kommentar
# ─── Linjene over tillater import som vanlig fra pages mappen ────────────────────────────────────────────────────────────────────────
<<<<<<< HEAD:src/app.py
from flask import Flask, render_template
from pages import overview

app = Flask(__name__)


# Her defineres routes ikke skriv funksjoner her, lag en egen fil i pages og importer derfra.

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/overview")
def overviewpage():
    return overview.helloOverview()












=======
>>>>>>> 1e6a36234907c2532a013be03640296f43556c96:src/app.py

from safecoin import app

if __name__ == '__main__':
    app.run(debug=True)
