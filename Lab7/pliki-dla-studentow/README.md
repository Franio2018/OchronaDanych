# Laboratorium 7 - SQL Injection i Code Injection

Poprawiona wersja celowo podatnej aplikacji „Sejf sekretów” (Flask + SQLite).
Zawiera łatki na SQL Injection (`/sekret`) i Code Injection (`/kalkulator`).

Aplikacja służy wyłącznie do lokalnej nauki. Baza zawiera dane fikcyjne.
Atakuj i testuj tylko to lokalne środowisko.

## Wymagania

- Docker z kontenerami Linux + Docker Compose (Windows: Docker Desktop z WSL 2).
- `curl` (Windows: `curl.exe`).

## Uruchomienie

Wszystkie polecenia w katalogu `pliki-dla-studentow` (tam, gdzie `compose.yaml`):

```bash
docker compose up -d --build
curl -i "http://127.0.0.1:8080/sekret?klucz=1234"        # HTTP 200, 1 wiersz, "Hello world"
curl -i "http://127.0.0.1:8080/kalkulator?wyrazenie=2*21" # HTTP 200, wynik 42
docker compose logs --tail 30 web                         # logi serwera
docker compose down                                       # zatrzymanie
```

Aplikacja działa pod `http://127.0.0.1:8080` (tylko pętla lokalna). Zajęty port zmień
w pliku `.env`: `LAB07_PORT=18080`. Po każdej zmianie w `aplikacja/` wykonaj
`docker compose restart web`. Kontener działa jako użytkownik `app` (UID 1000),
z systemem plików tylko do odczytu - to celowe ograniczenie skutków ataku.

Znaki `'`, `#`, `+`, spacje koduj przez formularz albo:
```bash
curl -G --data-urlencode "klucz=..."     http://127.0.0.1:8080/sekret
curl -G --data-urlencode "wyrazenie=2+3" http://127.0.0.1:8080/kalkulator
```

## Wprowadzone poprawki (`aplikacja/app.py`)

### Zadanie 1 i 2 - SQL Injection -> zapytanie z parametrem
Klucz był sklejany z treścią zapytania, więc apostrof i `UNION SELECT` zmieniały jego
strukturę (wyciek wszystkich sekretów i tabeli `konta`). Poprawka: stała treść SQL,
a wartość przekazana osobno jako parametr `?`. Szczegóły błędu SQLite trafiają do logu
serwera (`app.logger.exception`), użytkownik dostaje tylko ogólny komunikat.

```python
zapytanie = "SELECT wlasciciel, sekret FROM sekrety WHERE klucz = ?"
wiersze = db.execute(zapytanie, (klucz,)).fetchall()
```

Wartość parametru jest traktowana jako dane (łącznie z apostrofem, np. klucz `d'Artagnan`
działa poprawnie) i nie może zmienić składni. Parametr **nie** zastępuje nazwy tabeli ani
kolumny - te pozostają na stałe w kodzie.

### Zadanie 3 - Code Injection -> własny parser
`eval(wyrazenie)` pozwalał wykonać dowolny kod Pythona (`__import__('os').getuid()`,
`open('/etc/os-release').read()`, `os.listdir('/etc')`). Poprawka: parser przyjmujący
wyłącznie format „liczba operator liczba” (liczby ujemne i dziesiętne, spacje wokół
operatora), operatory `+ - * /` ze słownika, limit 100 znaków, obsługa dzielenia przez
zero. Bez `eval`, `exec`, `compile`. Złe wejście, puste pole i dzielenie przez zero
zwracają HTTP 400; `/kalkulator` bez parametru pokazuje sam formularz (HTTP 200).

Lista dozwolonych działań jest bezpieczniejsza niż blokowanie słów (np. `import`),
bo zakaz pojedynczych słów zawsze da się obejść innym wyrażeniem.

## Weryfikacja

Wyniki ataków i testów (przed i po poprawce) są w `dowody.md`, zwięzły raport w `RAPORT.md`.

## Struktura

- `aplikacja/app.py` - poprawiona aplikacja Flask.
- `aplikacja/templates/` - szablony HTML (bez zmian).
- `Dockerfile`, `compose.yaml`, `utworz_baze.py` - środowisko (bez zmian).
- `START.md`, `PRZEWODNIK.md` - instrukcje prowadzącego.
- `RAPORT.md`, `dowody.md` - raport i dowody.
