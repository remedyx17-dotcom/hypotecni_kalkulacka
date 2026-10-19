"""Webová vrstva (Flask) – on-line hypoteční kalkulačka."""
from flask import Flask, render_template, request

from calculator import Vstup, validuj, vypocitej

app = Flask(__name__)

POLE = {
    "prijem": "Příjem", "vydaje": "Výdaje", "splatky": "Splátky úvěrů",
    "cena": "Cena nemovitosti", "vlastni": "Vlastní zdroje",
    "urok": "Úroková sazba", "roky": "Doba splácení",
}
DEFAULTY = {"prijem": "55000", "vydaje": "20000", "splatky": "0",
            "cena": "5000000", "vlastni": "1000000", "urok": "4.9", "roky": "30"}


def nacti_formular(form):
    """Převede hodnoty z formuláře na čísla; vrátí (Vstup | None, chyby)."""
    hodnoty, chyby = {}, []
    for klic, nazev in POLE.items():
        try:
            hodnoty[klic] = float(form.get(klic, "").replace(",", ".").replace(" ", ""))
        except ValueError:
            chyby.append(f"Pole „{nazev}“ musí být číslo.")
    if chyby:
        return None, chyby
    hodnoty["roky"] = int(hodnoty["roky"])
    return Vstup(**hodnoty), []


@app.route("/", methods=["GET", "POST"])
def index():
    hodnoty, chyby, vysledek = DEFAULTY, [], None
    if request.method == "POST":
        hodnoty = request.form
        vstup, chyby = nacti_formular(request.form)
        if vstup:
            chyby = validuj(vstup)
            if not chyby:
                vysledek = vypocitej(vstup)
    return render_template("index.html", h=hodnoty, chyby=chyby, v=vysledek)


@app.template_filter("kc")
def kc(x):
    return f"{round(x):,}".replace(",", "\u00a0") + "\u00a0Kč"


if __name__ == "__main__":
    app.run(debug=True)
