# Laboratorium 4 — Funkcje skrótu

Język: Python 3.12. Tylko biblioteka standardowa: `hashlib` (SHA-256, PBKDF2-HMAC-SHA256),
`hmac.compare_digest` (porównanie w stałym czasie), `secrets` (losowanie soli).

Uruchomienie (z katalogu `Lab4`):

```
python sumy.py ["pliki-dla-studentow/SHA256SUMS.txt"]   # Zadanie 1 — sumy kontrolne
python hasla.py ["pliki-dla-studentow/hasla.txt"]       # Zadanie 2 — weryfikacja haseł
python kolizje.py ["pliki-dla-studentow"]               # Zadanie 3 — kolizje h24
```

Na Windowsie przy błędach kodowania polskich znaków w konsoli: `set PYTHONIOENCODING=utf-8`.
Wydruki programów są w katalogu `generated/`.
