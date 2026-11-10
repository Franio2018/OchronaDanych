# Laboratorium 4 — Funkcje skrótu — raport

## Zadanie 1 — Sumy kontrolne (`sumy.py`)

| Plik                        | Status |
|-----------------------------|--------|
| `dokumenty/budzet.csv`      | BŁĄD   |
| `dokumenty/dane.bin`        | OK     |
| `dokumenty/harmonogram.txt` | BRAK   |
| `dokumenty/kontakt.txt`     | OK     |
| `dokumenty/regulamin.txt`   | OK     |

Statusy zgodne z `sha256sum -c SHA256SUMS.txt`. SHA-256 `Ala ma kota.` i `Ola ma kota.` różnią się
w **131 z 256 bitów** (efekt lawinowy, ok. połowa).

**Wyjaśnienie:** kto może podmienić plik, może też podmienić leżącą obok sumę (SHA-256 nie ma klucza i każdy
może ją przeliczyć), więc przed celową podmianą chroni dopiero HMAC z tajnym kluczem albo podpis cyfrowy
(lub suma pobrana z niezależnego, zaufanego źródła).

## Zadanie 2 — Przechowywanie haseł (`hasla.py`)

PBKDF2-HMAC-SHA256 z parametrami rekordu, porównanie `hmac.compare_digest`.

| Login, hasło              | Wynik  | Oczekiwano |
|---------------------------|--------|------------|
| `anna`, `Kasztan-2026`    | prawda | prawda     |
| `anna`, `kasztan-2026`    | fałsz  | fałsz      |
| `piotr`, `Żółw na łące`   | prawda | prawda     |
| `kasia`, `Kasztan-2026`   | fałsz  | fałsz (nieznany login) |

Konta `test1` i `test2` z tym samym hasłem (sól 16 B z `secrets`, 600000 iteracji): **sole różne, skróty
różne**; weryfikacja obu kont: **prawda / prawda**.

**Wyjaśnienie:** losowa sól sprawia, że to samo hasło daje różne skróty na różnych kontach, więc nie widać
równych haseł i nie da się użyć gotowych tablic ani łamać wielu kont jednym przebiegiem; liczba iteracji
zwiększa koszt każdej próby hasła (spowalnia atak słownikowy/siłowy proporcjonalnie do liczby iteracji).

## Zadanie 3 — Kolizje i paradoks urodzinowy (`kolizje.py`)

h24 oryginału (wariant 0): `9a8fd6`.

- **Para kolizyjna:** v_oryginał = **7282**, v_zmieniony = **1761**, h24 = **`aac6b9`**.
- **Krok 3:** **0** z 8192 wariantów zmienionego dokumentu ma h24 równy h24 niezmienionego oryginału
  (oczekiwanie 8192 / 2²⁴ ≈ 0,0005).

**Wyjaśnienie:** przy dopasowaniu do jednego ustalonego skrótu każdy wariant ma szansę 1/2²⁴, więc potrzeba
ok. 2²⁴ prób, a przy szukaniu dowolnej pary porównujemy każdy z k wariantów z k wariantami drugiej strony —
k·k par, więc kolizja pojawia się już przy k ≈ 2¹² (paradoks urodzinowy, koszt ok. 2^(n/2)).

*Dodatkowo:* wszystkich par kolizyjnych 3 (oczekiwane 8192·8192/2²⁴ = 4); `dane.bin` liczony w kawałkach po
4096 B daje ten sam skrót; rekordy z < 600000 iteracji: `marek`, `zofia`; PBKDF2: 6,4 µs (1 iter.),
605 ms (600000 iter.) → 26⁶ haseł: ok. 33 min vs ok. 5,9 roku na jeden rekord.
