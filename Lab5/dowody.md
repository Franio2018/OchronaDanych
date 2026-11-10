# Dowody - Laboratorium 5 (Bezpieczenstwo serwera WWW)

Srodowisko: `docker compose up -d web`, serwer `http://127.0.0.1:8080`
(Apache/2.4.69, Python 3). Haslo konta `student` jest cwiczeniowe i lokalne -
w dowodach zapisane jako `HASLO`. Po kazdej zmianie: `httpd -t` -> `Syntax OK`,
nastepnie `docker compose restart web`.

---

## Zadanie 1 - dostep do katalogow

Reguly: `konfiguracja/dostep.conf` (sekcje `materialy` i `wewnetrzne`).

| Adres | Kod PRZED | Kod PO |
|---|---|---|
| `/materialy/` | 200 (widoczna lista plikow) | 403 |
| `/materialy/notatka.txt` | 200 | 200 |
| `/wewnetrzne/` | 200 | 403 |
| `/wewnetrzne/plan.txt` | 200 | 403 |

Przed zmiana `/materialy/` zwracalo autoindex: `<title>Index of /materialy</title>`.

Wpis z logu potwierdzajacy odmowe (po zmianie):

```
[authz_core:error] AH01630: client denied by server configuration:
/usr/local/apache2/htdocs/wewnetrzne/plan.txt
172.18.0.1 - - "GET /wewnetrzne/plan.txt HTTP/1.1" 403 239
```

Polecenia:

```
curl.exe -i http://127.0.0.1:8080/materialy/
curl.exe -i http://127.0.0.1:8080/materialy/notatka.txt
curl.exe -i http://127.0.0.1:8080/wewnetrzne/
curl.exe -i http://127.0.0.1:8080/wewnetrzne/plan.txt
docker compose logs --tail 30 web
```

---

## Zadanie 2 - katalog panel na haslo (HTTP Basic)

Konto: `docker compose run --rm --no-deps narzedzia -cB /auth/uzytkownicy student`
(haslo podane interaktywnie; plik `auth/uzytkownicy` poza htdocs i poza gitem).
Regula Basic na `/usr/local/apache2/htdocs/panel`, obszar `Laboratorium 5`.

| Proba (`/panel/raport.txt`) | Kod HTTP |
|---|---|
| bez danych logowania | 401 |
| bledne haslo | 401 |
| poprawne haslo | 200 |
| strona publiczna `/` | 200 |

Naglowek przy odpowiedzi bez logowania:

```
WWW-Authenticate: Basic realm="Laboratorium 5"
```

Polecenia:

```
curl.exe -i http://127.0.0.1:8080/panel/raport.txt
curl.exe -i -u student:HASLO http://127.0.0.1:8080/panel/raport.txt
curl.exe -i http://127.0.0.1:8080/
```

---

## Zadanie 3 - uprawnienia programu CGI

Skrypt: `cgi-bin/uprawnienia.cgi` (Python 3, konce wierszy LF). Po zmianie kodu:
`docker compose up -d --build web`.

Tozsamosc procesu CGI: **EUID = 2, EGID = 2** (uzytkownik/grupa `daemon`).

Wlasciciele i prawa (`docker compose exec web ls -ln /lab-data/`):

```
-rw-r-----  1 0 2  48  ogolny.txt     # 640  owner root(0), grupa daemon(2)
-rw-------  1 0 2  61  poufny.txt     # 600  tylko owner root(0)
```

Wyniki odczytu przez CGI:

| Plik | Prawa | Wynik odczytu przez CGI (daemon) |
|---|---|---|
| `/lab-data/ogolny.txt` | 640 root:daemon | ODCZYTANY (grupa daemon ma prawo `r`) |
| `/lab-data/poufny.txt` | 600 root:daemon | ODMOWA (PermissionError) - obsluzona, HTTP 200 |

Kody HTTP dla `/cgi-bin/uprawnienia.cgi`:

| Stan | Kod HTTP | EUID/EGID | Odczyty |
|---|---|---|---|
| przed Basic | 200 | 2 / 2 | ogolny OK, poufny odmowa |
| po Basic, bez logowania | 401 | - | - |
| po Basic, poprawne haslo | 200 | 2 / 2 | ogolny OK, poufny odmowa |

Po wlaczeniu Basic UID/GID i wyniki odczytow nie zmienily sie.

Polecenia:

```
curl.exe -i http://127.0.0.1:8080/cgi-bin/uprawnienia.cgi
docker compose exec web ls -ln /lab-data/
curl.exe -i -u student:HASLO http://127.0.0.1:8080/cgi-bin/uprawnienia.cgi
```
