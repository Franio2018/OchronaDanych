# Laboratorium 6 - Tablica ogłoszeń (XSS) - wersja poprawiona

Celowo podatna aplikacja Flask z laboratorium 6, **z naniesionymi poprawkami** trzech
podatności XSS. Uruchamiaj wyłącznie lokalnie, w kontenerze z pakietu.

## Uruchomienie

W tym katalogu (zawierającym `compose.yaml`):

```bash
docker compose build
docker compose up -d
```

- Aplikacja: http://127.0.0.1:8080
- Zbieracz (serwer napastnika, log żądań): http://localhost:8081 - `docker compose logs zbieracz`
- Logi aplikacji: `docker compose logs --tail 30 web`
- Po zmianie kodu w `aplikacja/`: `docker compose restart web`
- Zatrzymanie: `docker compose down`

Konta ćwiczeniowe: `anna` / `anna-lab6` (ofiara), `student` / `student-lab6` (napastnik).

## Wprowadzone poprawki

1. **XSS odbity** (`app.py`, trasa `/szukaj`) - parametr `q` kodowany przez `html.escape`.
2. **XSS zapisany / przejęcie sesji** (`app.py`) - `SESSION_COOKIE_HTTPONLY = True`
   oraz usunięty filtr `|safe` w `templates/tablica.html` (przywrócone kodowanie Jinja2).
3. **DOM XSS i CSP** (`/podglad`) - skrypt przeniesiony do `static/podglad.js`,
   `innerHTML` zamieniony na `textContent`; nagłówek
   `Content-Security-Policy: default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'self'`
   dodany przez `@app.after_request`.

Opis ataków, ładunków i dowodów: `../raport.md` oraz `../dowody.md`.

> Uwaga: hasła i klucz podpisu są jawne ćwiczeniowo. Poprawienie XSS nie stanowi
> pełnego audytu aplikacji do wdrożenia.
