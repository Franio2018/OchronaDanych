# Laboratorium 3 — Szyfrowanie blokowe — raport

Imię i nazwisko: **[UZUPEŁNIJ]** · Nr indeksu: **[UZUPEŁNIJ]** · Język: **Python 3.12** (biblioteka `cryptography`)
Repozytorium: **[LINK DO GITHUB]** · Commit: **[ID COMMITU]**

## Zadanie 1 — ECB i CBC (`ecb_cbc.py`)

Wejście `0123456789ABCDEF` × 4 (64 B), klucz `000102030405060708090a0b0c0d0e0f`, bez dopełnienia.

- **ECB:** wszystkie cztery bloki równe (1=2=3=4): `a5ba2b6280d433bccfe6a0461cb88c4e`.
- **CBC** (losowy IV): brak równych bloków — wszystkie cztery różne.
- Odszyfrowanie ECB == wejście: **OK**; odszyfrowanie CBC (pierwotny IV) == wejście: **OK**.

**Wyjaśnienie:** ECB szyfruje każdy blok niezależnie tym samym kluczem (`C[i] = AES_K(P[i])`), więc równe
bloki jawne dają równe bloki kryptogramu, a w CBC każdy blok jest przed szyfrowaniem XOR-owany z poprzednim
blokiem kryptogramu (pierwszy z IV), więc te same dane wejściowe dają różne wyniki.

## Zadanie 2 — Szyfrowanie z hasłem (`haslo.py`)

PBKDF2-HMAC-SHA256, 200000 iteracji, klucz 32 B, losowa sól 16 B, osobny losowy IV 16 B, AES-256-CBC + PKCS#7.

| Test           | Dane  | Kryptogram | Bajty po odszyfrowaniu |
|----------------|-------|------------|------------------------|
| puste dane     | 0 B   | 16 B       | zgodne — OK            |
| `0123456789ABCDEF` | 16 B | 32 B   | zgodne — OK            |
| `wiadomosc.txt`| 247 B | 256 B      | zgodne — OK            |

Dwukrotne szyfrowanie `wiadomosc.txt` tym samym hasłem, z nową solą i IV: **kryptogramy różne**, oba
odszyfrowują się poprawnie do oryginału.

**Sól a IV:** sól jest wejściem PBKDF2 i sprawia, że z tego samego hasła powstaje inny klucz (utrudnia
gotowe tablice i ataki na wiele haseł naraz), a IV nie zmienia klucza, tylko rozpoczyna łańcuch CBC, by te same
dane z tym samym kluczem dawały inny kryptogram. Sól i IV mogą być jawne; CBC nie zapewnia integralności.

## Zadanie 3 — Odzyskanie słabego klucza (`slaby_klucz.py`)

36 kluczy, próbka 4096 B, entropia po surowych bajtach, bez usuwania dopełnienia z próbki.

| Poz. | Znak | H      |
|------|------|--------|
| 1    | `m`  | 4.4536 |
| 2    | `b`  | 7.9472 |
| 3    | `x`  | 7.9490 |
| 4    | `o`  | 7.9493 |
| 5    | `2`  | 7.9502 |

**Klucz: `m` × 16** (`mmmmmmmmmmmmmmmm`). Po usunięciu PKCS#7: 13317 B, 100% znaków drukowalnych.
Pierwszy wiersz: `Record 000. The archive contains laboratory notes about symmetric encryption and careful handling of binary files.`

**Wniosek:** klucz to jeden znak z 36-elementowego alfabetu powtórzony 16 razy, więc wybieramy tylko jedną
wartość (36 możliwości, ok. 5,2 bita) zamiast 16 niezależnych bajtów (2^128); ranking entropii może zawieść dla
danych skompresowanych, bo poprawnie odszyfrowany tekst jawny też ma wtedy entropię bliską 8 bit/bajt i nie
odróżnia się od wyników błędnych kluczy.
