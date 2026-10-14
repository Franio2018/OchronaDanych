import os
import sys


def szyfruj_bajty(dane: bytes, klucz: bytes) -> bytes:
    """Szyfrowanie Vigenere'a na poziomie bajtów: c[i] = (p[i] + K[i % m]) % 256."""
    if len(klucz) == 0:
        raise ValueError("Klucz nie może być pusty")
    m = len(klucz)
    return bytes([(b + klucz[index % m]) % 256 for index, b in enumerate(dane)])


def odszyfruj_bajty(dane: bytes, klucz: bytes) -> bytes:
    """Odszyfrowanie Vigenere'a: p[i] = (c[i] - K[i % m]) % 256."""
    if len(klucz) == 0:
        raise ValueError("Klucz nie może być pusty")
    m = len(klucz)
    return bytes([(b - klucz[index % m]) % 256 for index, b in enumerate(dane)])


def sformatuj_hex_3x5(kryptogram: bytes) -> str:
    """Dzieli 15-bajtowy kryptogram na 3 fragmenty po 5 bajtów (szesnastkowo)."""
    return " ".join(kryptogram[i:i + 5].hex() for i in range(0, len(kryptogram), 5))


def testy():
    """Testy odwracalności: puste dane oraz dane zawierające bajty 0 i 255."""
    print("\n--- TESTY ---")
    klucz = b"ZAMEK"
    przypadki = {
        "puste dane": b"",
        "bajty 0 i 255": bytes([0, 255, 0, 255, 128, 1, 254]),
        "wszystkie bajty 0-255": bytes(range(256)),
    }
    for nazwa, dane in przypadki.items():
        zaszyfrowane = szyfruj_bajty(dane, klucz)
        wynik = odszyfruj_bajty(zaszyfrowane, klucz) == dane
        print(f"Test '{nazwa}': {'OK' if wynik else 'BŁĄD'} | szyfrogram: {repr(zaszyfrowane[:16])}")


def zadanie_brama():
    """Zadanie 2.2 - szyfrowanie BRAMABRAMABRAMA kluczami SZYFR i KOD."""
    tekst_jawny = b"BRAMABRAMABRAMA"

    print("\n--- BRAMABRAMABRAMA ---")
    for klucz in (b"SZYFR", b"KOD"):
        kryptogram = szyfruj_bajty(tekst_jawny, klucz)
        print(f"Klucz {klucz.decode('ascii'):5}: {sformatuj_hex_3x5(kryptogram)}")


def szyfrowanie_vigenera(sciezka_wejsciowa):
    key = b"ZAMEK"

    try:
        with open(sciezka_wejsciowa, "rb") as file:
            dane_wejsciowe = file.read()
    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku wejściowego w ścieżce: {sciezka_wejsciowa}")
        return

    zaszyfrowany_text = szyfruj_bajty(dane_wejsciowe, key)

    os.makedirs("generated", exist_ok=True)
    sciezka_wyjsciowa = os.path.join("generated", "vigenere.bin")

    with open(sciezka_wyjsciowa, "wb") as out_file:
        out_file.write(zaszyfrowany_text)

    print(f"[SUKCES] Zapisano zaszyfrowany plik (klucz {key.decode('ascii')}): {sciezka_wyjsciowa}")
    print(f"Początek szyfrogramu: {repr(zaszyfrowany_text[:50])}")

    # Odszyfrowanie zapisanego pliku i porównanie ze źródłem bajt po bajcie
    with open(sciezka_wyjsciowa, "rb") as file:
        odszyfrowane = odszyfruj_bajty(file.read(), key)

    zgodne = len(odszyfrowane) == len(dane_wejsciowe) and all(
        a == b for a, b in zip(odszyfrowane, dane_wejsciowe)
    )
    print(f"Zgodność odszyfrowania ze źródłem ({len(dane_wejsciowe)} B): {'OK' if zgodne else 'BŁĄD'}")


if __name__ == "__main__":
    sciezka = sys.argv[1] if len(sys.argv) > 1 else os.path.join("zadanie", "tekst_pl.txt")
    szyfrowanie_vigenera(sciezka)
    testy()
    zadanie_brama()
