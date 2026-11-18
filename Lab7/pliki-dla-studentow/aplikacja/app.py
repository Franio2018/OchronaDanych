"""Sejf sekretow i kalkulator - wersja poprawiona do laboratorium 7.

Poprawki:
- /sekret: zapytanie z parametrem ? zamiast sklejania napisu (SQL Injection),
  ogolny komunikat dla uzytkownika, szczegoly do logu serwera.
- /kalkulator: wlasny parser zamiast eval (Code Injection),
  dozwolony format "liczba operator liczba", HTTP 400 dla zlego wejscia.

Uruchamiaj wylacznie lokalnie, w kontenerze z pakietu. Dane sa fikcyjne.
"""
import re
import sqlite3

from flask import Flask, render_template, request

app = Flask(__name__)
BAZA = "file:/dane/sekrety.db?mode=ro"

# Zadanie 3: parser kalkulatora.
# Dozwolony format: liczba operator liczba. Liczba moze byc ujemna i miec
# czesc dziesietna; wokol operatora moga byc spacje. Dozwolone operatory: + - * /.
WZORZEC = re.compile(r"\s*(-?\d+(?:\.\d+)?)\s*([+\-*/])\s*(-?\d+(?:\.\d+)?)\s*")
DZIALANIA = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a / b,
}


def oblicz(wyrazenie):
    """Liczy wyrazenie po walidacji. Przy zlym wejsciu zglasza ValueError."""
    if len(wyrazenie) > 100:
        raise ValueError("Wejscie za dlugie")
    dopasowanie = re.fullmatch(WZORZEC, wyrazenie)
    if dopasowanie is None:
        raise ValueError("Nieprawidlowe wyrazenie")
    lewy = float(dopasowanie.group(1))
    operator = dopasowanie.group(2)
    prawy = float(dopasowanie.group(3))
    if operator == "/" and prawy == 0:
        raise ValueError("Dzielenie przez zero")
    return DZIALANIA[operator](lewy, prawy)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/sekret")
def sekret():
    klucz = request.args.get("klucz", "")
    # Zadanie 2: stala tresc zapytania, wartosc przekazana osobno jako parametr.
    # Parametr zastepuje tylko wartosc; nazwa tabeli i kolumn pozostaje w kodzie.
    zapytanie = "SELECT wlasciciel, sekret FROM sekrety WHERE klucz = ?"
    wiersze, blad = [], None
    try:
        with sqlite3.connect(BAZA, uri=True) as db:
            wiersze = db.execute(zapytanie, (klucz,)).fetchall()
    except sqlite3.Error:
        # Szczegoly do logu serwera, uzytkownik dostaje ogolny komunikat.
        app.logger.exception("Blad zapytania /sekret dla klucza %r", klucz)
        blad = "Wystapil blad podczas wyszukiwania."
    return render_template("sekret.html", klucz=klucz, zapytanie=zapytanie, wiersze=wiersze, blad=blad)


@app.route("/kalkulator")
def kalkulator():
    wyrazenie = request.args.get("wyrazenie")
    # Brak parametru -> tylko formularz (HTTP 200).
    if wyrazenie is None:
        return render_template("kalkulator.html", wyrazenie="", wynik=None)
    # Puste pole i zle wejscie -> HTTP 400 z krotkim komunikatem.
    try:
        wynik = oblicz(wyrazenie)
    except ValueError as exc:
        return f"Nieprawidlowe dane: {exc}", 400
    return render_template("kalkulator.html", wyrazenie=wyrazenie, wynik=wynik)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
