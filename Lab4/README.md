# Laboratorium 5 — Kontrola dostępu w Apache (HTTP Basic + prawa plików)

Serwer `httpd:2.4-alpine` z Pythonem 3 do CGI, uruchamiany przez Docker Compose.
Port wystawiony wyłącznie na `127.0.0.1:8080`. Nie używać prawdziwych haseł.

## Wymagania

Docker z kontenerami Linux i Docker Compose (w Windows: Docker Desktop z WSL 2),
przeglądarka oraz `curl` (w Windows `curl.exe`). Wszystkie komendy z katalogu `Lab4/`.

## Uruchomienie

```
docker compose build web
docker compose up -d web
docker compose exec web httpd -t      # oczekiwane: Syntax OK
curl -i http://127.0.0.1:8080/        # oczekiwane: HTTP 200, "serwer WWW działa"
docker compose logs --tail 30 web
docker compose down
```

Zajęty port: w `.env` ustaw `LAB05_PORT=18080` i używaj tego portu w adresach.
Baza haseł powstaje narzędziem `htpasswd` z profilu `narzedzia`:

```
docker compose run --rm narzedzia -Bbc /auth/uzytkownicy student haslo
```

## Co edytuję na zajęciach

- `konfiguracja/dostep.conf` — własne reguły dostępu (montowane do kontenera;
  po zmianie: `httpd -t`, potem `docker compose restart web`).
- `cgi-bin/uprawnienia.cgi` — własny program CGI (trafia do obrazu podczas budowy;
  po zmianie: `docker compose up -d --build web`). Zapis z końcami wierszy LF,
  nagłówek `Content-Type` i pusta linia przed treścią.

## Struktura (host → kontener)

| Host | Kontener |
|---|---|
| `www/` | `/usr/local/apache2/htdocs/` |
| `cgi-bin/` | `/usr/local/apache2/cgi-bin/` |
| `auth/` | `/auth/` |
| `dane/` | `/lab-data/` |
| `konfiguracja/dostep.conf` | `/usr/local/apache2/conf/dostep.conf` |

## Nie w repozytorium

`auth/*` (baza haseł) oraz `.env` są wykluczone przez `.gitignore`.
Dane w `dane/` są fikcyjne. Szczegóły zadań: `START.md` i `PRZEWODNIK.md`.
