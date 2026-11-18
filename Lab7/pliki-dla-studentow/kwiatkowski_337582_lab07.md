# Raport - Laboratorium 7: SQL Injection i Code Injection

**Imię i nazwisko:** Franciszek Kwiatkowski
**Nr indeksu:** 337582

Aplikacja „Sejf sekretów” (Flask + SQLite), `http://127.0.0.1:8080`. Poprawki w `aplikacja/app.py`.
Pełne ładunki i logi: `dowody.md`.

## Zadanie 1 - SQL Injection
Dziura: klucz sklejany z zapytaniem `... WHERE klucz = '"+klucz+"'`.

| Wejście | Wierszy |
|---|:--:|
| `1234` | 1 |
| `'` | 0 (błąd: niezamknięty literał) |
| `' OR '1'='1` | 4 |
| `' UNION SELECT name, sql FROM sqlite_master WHERE type='table' --` | 2 |
| `' UNION SELECT login, rola\|\|' '\|\|email FROM konta --` | 2 |

Zapytanie po wstawieniu (atak 3): `SELECT wlasciciel, sekret FROM sekrety WHERE klucz = '' OR '1'='1'`.
Druga tabela: **`konta`** (kolumny `login, rola, email`).
Wniosek: apostrof zamyka literał, a `OR`/`UNION`/`--` są interpretowane jako składnia SQL - dane zmieniają strukturę zapytania.

## Zadanie 2 - Zapytanie z parametrami
Poprawka: stałe `WHERE klucz = ?` + wartość w krotce; ogólny komunikat, szczegóły przez `app.logger.exception`.

| Wejście | Przed | Po |
|---|:--:|:--:|
| `1234` | 1 | 1 |
| `'` | 0 (błąd) | 0 |
| `' OR '1'='1` | 4 | 0 |
| UNION schematu | 2 | 0 |
| UNION `konta` | 2 | 0 |
| `d'Artagnan` | 0 (błąd) | 1 |

Wniosek: wartość parametru idzie do bazy osobno od treści SQL i jest traktowana jako dane, więc nie zmienia struktury zapytania. Parametr **nie** zastępuje nazwy tabeli - tę wybiera się z listy w kodzie.

## Zadanie 3 - Code Injection w kalkulatorze
Dziura: `eval(wyrazenie)`. Ataki (pole `wyrazenie`): `__import__('os').listdir('/etc')`, `open('/etc/os-release').read()` (Alpine Linux), `__import__('os').getuid()` -> UID **1000** (użytkownik `app`, nie root).
Poprawka: własny parser „liczba operator liczba”, limit 100 znaków, słownik operatorów, obsługa dzielenia przez zero; bez `eval/exec/compile`.

| Test | HTTP | Wynik |
|---|:--:|---|
| `2+3` | 200 | 5.0 |
| `7 / 2` | 200 | 3.5 |
| `-1.5*4` | 200 | -6.0 |
| `1/0` | 400 | dzielenie przez zero |
| `__import__('os').listdir('/etc')` | 400 | odrzucone |
| `open('/etc/os-release').read()` | 400 | odrzucone |
| `__import__('os').getuid()` | 400 | odrzucone |
| puste `?wyrazenie=` | 400 | odrzucone |

Wniosek: lista dozwolonych działań przepuszcza tylko znane operacje, a blokowanie słów (np. `import`) zawsze da się obejść innym wyrażeniem - dlatego allowlist jest bezpieczniejsza.
