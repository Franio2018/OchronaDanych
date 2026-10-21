# Laboratorium 3 — Szyfrowanie blokowe

Język: Python 3.12. Wymagana biblioteka: `cryptography` (AES, PBKDF2, PKCS#7).

```
pip install cryptography
```

Uruchomienie (z katalogu `Lab3`):

```
python ecb_cbc.py                              # Zadanie 1 — ECB i CBC
python haslo.py ["zadanie 3/wiadomosc.txt"]    # Zadanie 2 — szyfrowanie z hasłem
python slaby_klucz.py ["zadanie 3/slaby_ecb.bin"]  # Zadanie 3 — odzyskanie słabego klucza
```

Wydruki programów są w katalogu `generated/`, odszyfrowany tekst z zadania 3 w `generated/slaby_ecb.txt`.
