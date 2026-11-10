#!/usr/bin/python3
# CGI zadania 3: pokazuje efektywna tozsamosc procesu (EUID/EGID) i probuje
# odczytac dwa pliki danych. Odmowe odczytu przechwytujemy jako wyjatek, aby
# odpowiedz HTTP powstala w calosci (bez bledu 500).
import os

# Naglowek CGI, pusta linia, potem tresc tekstowa.
print("Content-Type: text/plain; charset=utf-8")
print()

print("Efektywna tozsamosc procesu CGI:")
print("  EUID = {}".format(os.geteuid()))
print("  EGID = {}".format(os.getegid()))
print()

for sciezka in ("/lab-data/ogolny.txt", "/lab-data/poufny.txt"):
    print("--- {} ---".format(sciezka))
    try:
        with open(sciezka, "r", encoding="utf-8") as f:
            print(f.read().rstrip("\n"))
    except OSError as e:
        print("ODMOWA ODCZYTU: {}: {}".format(type(e).__name__, e.strerror))
    print()
