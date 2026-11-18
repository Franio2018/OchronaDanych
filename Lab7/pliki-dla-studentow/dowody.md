# Dowody - Laboratorium 7 (SQL Injection i Code Injection)

Środowisko: `http://127.0.0.1:8080`, aplikacja „Sejf sekretów” (Flask + SQLite).
Schemat bazy: `sekrety(klucz, wlasciciel, sekret)` - 4 wiersze; `konta(login, rola, email)` - 2 wiersze.
Zapytanie sejfu zwraca **dwie** kolumny (`wlasciciel, sekret`).

Wejścia z apostrofem / spacją podawaj przez formularz albo:
`curl -G --data-urlencode "klucz=..." http://127.0.0.1:8080/sekret`

---

## Zadanie 1 - SQL Injection (wersja podatna)

Podatny kod: `SELECT wlasciciel, sekret FROM sekrety WHERE klucz = '" + klucz + "'`.

| # | Wejście (klucz) | Liczba wierszy | Uwagi |
|---|-----------------|:--:|-------|
| 1 | `1234` | 1 | legalny klucz |
| 2 | `'` | 0 (błąd) | `OperationalError: unrecognized token: "'''"` - niezamknięty literał |
| 3 | `' OR '1'='1` | 4 | warunek zawsze prawdziwy - wszystkie sekrety |
| 4 | `' UNION SELECT name, sql FROM sqlite_master WHERE type='table' --` | 2 | nazwy tabel + ich DDL |
| 5 | `' UNION SELECT login, rola\|\|' '\|\|email FROM konta --` | 2 | zawartość drugiej tabeli |

Zapytanie po wstawieniu danych (atak 3):
```sql
SELECT wlasciciel, sekret FROM sekrety WHERE klucz = '' OR '1'='1'
```

Wynik ataku 4 (nazwy tabel i ich definicje z kolumny `sql`):
`sekrety -> CREATE TABLE sekrety(klucz TEXT, wlasciciel TEXT, sekret TEXT)`
`konta  -> CREATE TABLE konta(login TEXT, rola TEXT, email TEXT)`

Druga tabela: **`konta`**, kolumny **`login, rola, email`** (ujawnione atakiem 5).

Jedno zdanie: apostrof w wejściu zamyka literał napisowy, a dalsza treść (`OR`, `UNION SELECT`, `--`)
jest interpretowana jako składnia SQL, więc dane zmieniają strukturę wykonywanego zapytania.

---

## Zadanie 2 - Zapytanie z parametrami (po poprawce)

Poprawka (`app.py`): stała treść zapytania + wartość w krotce, ogólny komunikat, log serwera.
```python
zapytanie = "SELECT wlasciciel, sekret FROM sekrety WHERE klucz = ?"
wiersze = db.execute(zapytanie, (klucz,)).fetchall()
except sqlite3.Error:
    app.logger.exception("Blad zapytania /sekret dla klucza %r", klucz)
    blad = "Wystapil blad podczas wyszukiwania."
```

| Wejście (klucz) | Wierszy PRZED | Wierszy PO |
|-----------------|:--:|:--:|
| `1234` | 1 | 1 |
| `'` | 0 (błąd SQLite) | 0 (brak dopasowania, bez błędu) |
| `' OR '1'='1` | 4 | 0 |
| `' UNION SELECT name, sql FROM sqlite_master WHERE type='table' --` | 2 | 0 |
| `' UNION SELECT login, rola\|\|' '\|\|email FROM konta --` | 2 | 0 |
| `d'Artagnan` | 0 (błąd składni) | 1 |

Po poprawce żaden atak nie zwraca danych ani komunikatu SQLite; legalny klucz z apostrofem
`d'Artagnan` działa poprawnie (1 wiersz).

Jedno zdanie: wartość parametru trafia do bazy osobno od treści SQL i jest traktowana jako
dane (łącznie z apostrofem), więc nie może dodać ani zmienić składni zapytania.
Parametr **nie** może zastąpić nazwy tabeli ani kolumny - te muszą pochodzić z ustalonej listy w kodzie.

---

## Zadanie 3 - Code Injection w kalkulatorze

Podatny kod: `wynik = eval(wyrazenie)`.

Ataki (tylko przez pole `wyrazenie`, kod aplikacji niezmieniony):

| Cel | Wyrażenie | Skrócony wynik |
|-----|-----------|----------------|
| katalog `/etc` | `__import__('os').listdir('/etc')` | `['os-release', 'passwd', 'group', 'hosts', ...]` |
| `/etc/os-release` | `open('/etc/os-release').read()` | `NAME="Alpine Linux"  VERSION_ID=3.x ...` |
| UID procesu | `__import__('os').getuid()` | `1000` (użytkownik `app`, nie root) |

curl: `curl -G --data-urlencode "wyrazenie=__import__('os').getuid()" http://127.0.0.1:8080/kalkulator`

Poprawka: własny parser (`oblicz`), format „liczba operator liczba”, limit 100 znaków,
operator ze słownika, obsługa dzielenia przez zero; bez `eval/exec/compile`.

| # | Wejście | HTTP | Wynik po poprawce |
|---|---------|:--:|-------------------|
| 1 | `2+3` | 200 | 5.0 |
| 2 | `7 / 2` | 200 | 3.5 |
| 3 | `-1.5*4` | 200 | -6.0 |
| 4 | `1/0` | 400 | Dzielenie przez zero |
| 5 | `__import__('os').listdir('/etc')` | 400 | Nieprawidłowe wyrażenie |
| 6 | `open('/etc/os-release').read()` | 400 | Nieprawidłowe wyrażenie |
| 7 | `__import__('os').getuid()` | 400 | Nieprawidłowe wyrażenie |
| 8 | puste pole `?wyrazenie=` | 400 | Nieprawidłowe wyrażenie |

Dodatkowo: `2+3abc` -> 400, wejście 101 znaków -> 400, `/kalkulator` bez parametru -> 200 (sam formularz).

Jedno zdanie: lista dozwolonych operacji akceptuje tylko znane, bezpieczne działania, podczas
gdy blokowanie słów (np. `import`) zawsze da się obejść innym wyrażeniem (`open`, `__import__`,
operatory `||` itp.), więc nie tworzy bezpiecznego kalkulatora.

Uwaga (lab 5): `/etc/shadow` jest nieczytelny dla UID użytkownika `app` - proces działa z
najmniejszymi uprawnieniami, co ogranicza skutki, ale samo w sobie nie usuwa Code Injection.
