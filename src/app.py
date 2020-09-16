# import sys
# sys.path.insert(0, '/pages')    #Dersom import ikke fungerer fjern kommentar
# ─── Linjene over tillater import som vanlig fra pages mappen ─────────────────────────────────────────────────────────
from safecoin import app

if __name__ == '__main__':
    app.run(debug=True)
