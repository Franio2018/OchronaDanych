import os

def szyfruj_bajty(dane: bytes, klucz_str: str) -> bytes:
    """Uniwersalna funkcja do szyfrowania Vigenere'a na poziomie bajtów (modulo 256)."""
    klucz_bytes = klucz_str.encode("utf-8")
    m = len(klucz_bytes)
    # Szyfrowanie to dodawanie (+) klucza do tekstu jawnego
    return bytes(
        [(b + klucz_bytes[index % m]) % 256 for index, b in enumerate(dane)]
    )


def sformatuj_hex_3x5(kryptogram: bytes) -> str:
    """Pomocnicza funkcja dzieląca 15-bajtowy kryptogram na 3 części po 5 bajtów."""
    hex_str = kryptogram.hex()
    # Dzielimy ciąg hex (30 znaków) na fragmenty po 10 znaków hex (5 bajtów)
    f1 = hex_str[0:10]
    f2 = hex_str[10:20]
    f3 = hex_str[20:30]
    return f"{f1} {f2} {f3}"


def zadanie_drugie():
    """Realizuje dodatkową część zadania z ciągiem BRAMABRAMABRAMA."""
    tekst_jawny = "BRAMABRAMABRAMA".encode("ascii")

    print("\n--- REALIZACJA DODATKOWEGO ZADANIA ---")

    # 1. Pierwsze szyfrowanie kluczem SZYFR
    kryptogram1 = szyfruj_bajty(tekst_jawny, "SZYFR")
    print(f"Kryptogram 1 (klucz SZYFR): {sformatuj_hex_3x5(kryptogram1)}")

    # 2. Drugie szyfrowanie pierwszego kryptogramu kluczem KOD
    kryptogram2 = szyfruj_bajty(kryptogram1, "KOD")
    print(f"Kryptogram 2 (klucz KOD):   {sformatuj_hex_3x5(kryptogram2)}")
    print("-" * 38)


def szyfrowanie_vigenera():
    key = "Zamek"
    sciezka_wejsciowa = os.path.join("zadanie", "tekst_pl.txt")

    try:
        with open(sciezka_wejsciowa, "rb") as file:
            dane_wejsciowe = file.read()
    except FileNotFoundError:
        print(
            f"Błąd: Nie znaleziono pliku wejściowego w ścieżce: {sciezka_wejsciowa}"
        )
        return

    rozmiar = len(dane_wejsciowe)
    if rozmiar == 0:
        print("Błąd: Plik jest pusty.")
        return

    # Szyfrowanie pliku za pomocą wspólnej funkcji
    zaszyfrowany_text = szyfruj_bajty(dane_wejsciowe, key)

    os.makedirs("generated", exist_ok=True)
    sciezka_wyjsciowa = os.path.join("generated", "vigenere.bin")

    # Zapis zaszyfrowanego tekstu
    with open(sciezka_wyjsciowa, "wb") as out_file:
        out_file.write(zaszyfrowany_text)

    print(
        f"\n[SUKCES] Zapisano pełny zaszyfrowany tekst dla klucza k={key} do pliku: {sciezka_wyjsciowa}"
    )


if __name__ == "__main__":
    szyfrowanie_vigenera()

    zadanie_drugie()