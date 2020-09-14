# import sys
# sys.path.insert(0, '/pages')    #Dersom import ikke fungerer fjern kommentar
# ─── Linjene over tillater import som vanlig fra pages mappen ────────────────────────────────────────────────────────────────────────
from flask import Flask, render_template
from pages import overview 

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")
  

@app.route("/overview")
def overviewpage():
    return overview.hello_overview()


if __name__ == '__main__':
    app.run(debug=True)
