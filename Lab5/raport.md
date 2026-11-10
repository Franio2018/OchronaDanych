# Laboratorium 5 - Bezpieczenstwo serwera WWW

**Imie i Nazwisko:** Franciszek Kwiatkowski
**Nr indeksu:** 337582

Srodowisko: Apache/2.4.69 + Python 3 w Dockerze, `http://127.0.0.1:8080`.
Szczegolowe polecenia, ladunki i logi: `dowody.md`.

## Zadanie 1 - dostep do katalogow

| Adres | Kod przed | Kod po |
|---|---|---|
| `/materialy/` | 200 (lista) | 403 |
| `/materialy/notatka.txt` | 200 | 200 |
| `/wewnetrzne/` | 200 | 403 |
| `/wewnetrzne/plan.txt` | 200 | 403 |

Log odmowy: `AH01630: client denied by server configuration: .../wewnetrzne/plan.txt`.

**Wniosek:** `Options -Indexes` wylacza tylko automatyczna liste plikow, wiec zasob
o znanym adresie nadal dziala; `Require all denied` blokuje caly dostep (403),
niezaleznie od znajomosci nazwy pliku.

## Zadanie 2 - katalog panel na haslo

| Proba (`/panel/raport.txt`) | Kod |
|---|---|
| bez logowania | 401 |
| bledne haslo | 401 |
| poprawne haslo | 200 |

`WWW-Authenticate` bez logowania: `Basic realm="Laboratorium 5"`.
Strona publiczna `/` nadal zwraca 200.

**Wniosek:** HTTP Basic przez zwykle HTTP nie chroni hasla w transmisji - jest ono
jedynie zakodowane w Base64 (nie zaszyfrowane), wiec kazdy, kto przechwyci ruch,
moze je odczytac; dopiero HTTPS/TLS szyfruje polaczenie.

## Zadanie 3 - uprawnienia programu CGI

Tozsamosc CGI: **EUID = 2, EGID = 2** (`daemon`).

| Plik | Prawa | Wlasciciel | Odczyt przez CGI |
|---|---|---|---|
| `ogolny.txt` | 640 | root:daemon | OK (grupa daemon czyta) |
| `poufny.txt` | 600 | root:daemon | odmowa (tylko root) |

| Stan `/cgi-bin/uprawnienia.cgi` | Kod |
|---|---|
| przed Basic | 200 |
| po Basic, bez logowania | 401 |
| po Basic, poprawne haslo | 200 (UID/GID i odczyty bez zmian) |

**Wniosek:** zalogowanie do serwera WWW autoryzuje tylko zadanie na poziomie HTTP;
proces CGI nadal dziala z systemowa tozsamoscia serwera (`daemon`), wiec o dostepie
do plikow decyduja prawa systemu plikow, a nie fakt uwierzytelnienia - Basic nie
daje praw administratora.
