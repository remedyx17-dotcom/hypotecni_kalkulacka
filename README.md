# Hypoteční kalkulačka (maturitní práce)

Spuštění:

    python -m venv venv
    venv\Scripts\activate        (Linux/macOS: source venv/bin/activate)
    pip install -r requirements.txt
    python app.py

Aplikace poběží na http://127.0.0.1:5000

Testy výpočtů:  python -m unittest discover tests

Struktura: calculator.py (logika), app.py (Flask), templates/, static/, tests/
