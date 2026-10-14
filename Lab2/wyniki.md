# Laboratorium 2 — Kryptografia historyczna — wyniki

## Zadanie 1. Cezar

Uruchomienie: `python cezar.py cezar.bin` (program prosi o wybór kandydata 1–5).

| Poz. | k   | Ocena   | Początek odszyfrowania                                   |
|------|-----|---------|----------------------------------------------------------|
| 1    | 230 | 100.00% | `b'Wkh#Qljkw#Ihuu\|\r\rWkh#qljkw#ihuu\|#ohiw#wkh#kduerxu#'` |
| 2    | 233 | 100.00% | `b'The Night Ferry\n\nThe night ferry left the harbour '`   |
| 3    | 228 | 99.48%  | `b'Ymj%Snlmy%Kjww~\x0f\x0fYmj%snlmy%kjww~%qjky%ymj%mfwgtzw%'` |
| 4    | 229 | 99.48%  | `b'Xli$Rmklx$Jivv}\x0e\x0eXli$rmklx$jivv}$pijx$xli$levfsyv$'` |
| 5    | 231 | 99.48%  | `b'Vjg"Pkijv"Hgtt{\x0c\x0cVjg"pkijv"hgtt{"nghv"vjg"jctdqwt"'` |

**Wybrane przesunięcie: k = 233.** Kandydaci 1 i 2 mają taką samą ocenę (100%), a remis rozstrzygnięto
według k, więc k = 230 jest wyżej. Jego wynik to jednak wciąż tekst przesunięty o 3 („Wkh Qljkw” = „The Night”
z szyfru Cezara), a spacje zamieniły się w `#`. Dopiero k = 233 daje sensowny angielski tekst („The Night Ferry”),
który zapisano w `cezar.txt`.

**Dlaczego entropia nie wystarczy:** przesunięcie o stałe k jest permutacją wartości 0–255, więc tylko zmienia
etykiety słupków histogramu, a nie ich wysokości. Entropia zależy wyłącznie od wysokości słupków, dlatego jest
identyczna dla wszystkich 256 kandydatów (np. dla k = 230 i k = 233 wynosi 4.2469 bit/bajt).

## Zadanie 2. Vigenère (bajtowy)

Uruchomienie: `python vigenere.py tekst_pl.txt`. Klucz ASCII `ZAMEK`, wynik zapisany w `vigenere.bin`.

Testy:
- odszyfrowanie `vigenere.bin` zgodne ze źródłem bajt po bajcie (2867 B): **OK**
- puste dane: **OK** (szyfrogram `b''`)
- dane zawierające bajty 0 i 255 (`00 ff 00 ff 80 01 fe`): **OK**
- wszystkie bajty 0–255: **OK**

Kryptogramy ciągu `BRAMABRAMABRAMA` (szesnastkowo, 3 × 5 bajtów):

```
SZYFR: 95ac9a9393 95ac9a9393 95ac9a9393
KOD  : 8da1859890 869d90918c 91968c9c85
```

**Wyjaśnienie:** słowo `BRAMA` i klucz `SZYFR` mają tę samą długość 5, więc każde powtórzenie słowa zaczyna się
w tym samym miejscu klucza i jest szyfrowane identycznie — trzy fragmenty kryptogramu są takie same.
Klucz `KOD` ma długość 3, a 5 nie jest wielokrotnością 3, więc kolejne `BRAMA` trafiają na przesunięte fragmenty
klucza (`KODKO`, `DKODK`, `ODKOD`) i dają różne bajty. Atakujący widzi w pierwszym przypadku powtórzenia w
kryptogramie i ich odstęp (5), co zdradza powtarzający się tekst i długość klucza (dzielnik odstępu, jak w metodzie Kasiskiego).

## Zadanie 3. RC4

Uruchomienie: `python rc4.py rc4.bin` (wymaga pakietów `tqdm` i `rich`).
Test odwracalności (dwukrotne zastosowanie z tym samym kluczem odtwarza wejście): **OK**.

Ranking (entropia pierwszych 512 bajtów, rosnąco):

| Poz. | Klucz | Entropia |
|------|-------|----------|
| 1    | `tat` | 4.3910   |
| 2    | `neg` | 7.4304   |
| 3    | `mcn` | 7.4512   |
| 4    | `oxo` | 7.4536   |
| 5    | `tnx` | 7.4592   |

- **Klucz:** `tat` (wybrany automatycznie jako pierwszy w rankingu)
- **Liczba prób:** 17 576 (26³, przeszukano wszystkie klucze)
- **Czas przeszukiwania:** ok. 5 s
- **Entropia całego kryptogramu:** 7.9271 bit/bajt
- **Entropia całego odszyfrowania:** 4.3259 bit/bajt
- Odszyfrowanie zaczyna się od „The Clockmaker's Apprentice”, 100% znaków drukowalnych — tekst sensowny.
- Ponowne zaszyfrowanie `rc4.txt` kluczem `tat` daje kryptogram identyczny z `rc4.bin`: **OK**

**Wyjaśnienie:** RC4 to szyfr strumieniowy oparty na XOR, więc dla dowolnego klucza `(C ⊕ S) ⊕ S = C` — ponowne
szyfrowanie zawsze odtwarza kryptogram, nawet dla błędnego klucza, i nie dowodzi poprawności wyboru.
Ranking entropii mógłby zawieść, gdy próbka jest zbyt krótka (entropia wtedy jest zaniżona dla każdego klucza),
gdy tekst jawny sam ma wysoką entropię (dane skompresowane, zaszyfrowane, losowe) albo gdy zostały odrzucone
lub pominięte początkowe bajty strumienia i odszyfrowanie startuje z niewłaściwej pozycji.
