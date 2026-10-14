import os
import sys


def analizuj_szyfr_cezara(sciezka_wejsciowa):
    try:
        with open(sciezka_wejsciowa, "rb") as file:
            dane_zaszyfrowane = file.read()
    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku wejściowego w ścieżce: {sciezka_wejsciowa}")
        return

    rozmiar = len(dane_zaszyfrowane)
    if rozmiar == 0:
        print("Błąd: Plik cezar.bin jest pusty.")
        return

    poprawne_bajty = set(range(32, 127)) | {9, 10, 13}
    kandydaci = []

    for k in range(256):
        odszyfrowane = bytes([(c - k) % 256 for c in dane_zaszyfrowane])

        liczba_tekstowych = sum(1 for b in odszyfrowane if b in poprawne_bajty)
        ocena = liczba_tekstowych / rozmiar

        kandydaci.append((ocena, k, odszyfrowane))

    # Sortowanie malejąco po ocenie, remisy rosnąco według k
    kandydaci.sort(key=lambda x: (-x[0], x[1]))

    print("=== PIĘCIU NAJLEPSZYCH KANDYDATÓW ===")
    for i, (ocena, k, odszyfrowane) in enumerate(kandydaci[:5]):
        # repr(), bo odszyfrowanie może zawierać znaki sterujące
        print(f"{i+1}. k = {k:3d} | Ocena: {ocena:7.2%} | Początek: {repr(odszyfrowane[:50])}")

    # Wybór ręczny kandydata spośród pięciu najlepszych
    wybor = input("\nPodaj numer kandydata (1-5) dającego sensowny tekst: ").strip()
    while wybor not in {"1", "2", "3", "4", "5"}:
        wybor = input("Niepoprawny numer, podaj 1-5: ").strip()

    _, wybrany_klucz, dane_odszyfrowane = kandydaci[int(wybor) - 1]

    os.makedirs("generated", exist_ok=True)
    sciezka_wyjsciowa = os.path.join("generated", "cezar.txt")

    # Zapis binarny - bez zmieniania odzyskanych bajtów
    with open(sciezka_wyjsciowa, "wb") as out_file:
        out_file.write(dane_odszyfrowane)

    print(f"\n[SUKCES] Zapisano pełny odszyfrowany tekst dla klucza k={wybrany_klucz} do pliku: {sciezka_wyjsciowa}")


if __name__ == "__main__":
    sciezka = sys.argv[1] if len(sys.argv) > 1 else os.path.join("zadanie", "cezar.bin")
    analizuj_szyfr_cezara(sciezka)
