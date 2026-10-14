import os

def analizuj_szyfr_cezara():
    sciezka_wejsciowa = "zadanie\\cezar.bin"
    
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
        odszyfrowane = bytes([(b - k) % 256 for b in dane_zaszyfrowane])
        
        liczba_tekstowych = sum(1 for b in odszyfrowane if b in poprawne_bajty)
        ocena = liczba_tekstowych / rozmiar
        
        podglad = ""
        for b in odszyfrowane[:45]:
            if 32 <= b <= 126:
                podglad += chr(b)
            elif b in (9, 10, 13):
                podglad += " "  # Zamiana białych znaków na spację w podglądzie
            else:
                podglad += "•"  # Reprezentacja znaku niedrukowalnego
                
        kandydaci.append((ocena, k, odszyfrowane, podglad))

    kandydaci.sort(key=lambda x: (-x[0], x[1]))

    print("=== PIĘCIU NAJLEPSZYCH KANDYDATÓW ===")
    for i, (ocena, k, _, podglad) in enumerate(kandydaci[:5]):
        print(f"Pozycja {i+1} | Klucz k = {k:3d} | Ocena: {ocena:6.2%} | Podgląd: {podglad}")

    # Program wybiera kandydata z pozycji 2 [Dla naszego przykładu był poprawny], 
    # w razie potrzeby można zmienić indeks, albo dodać wybór przez użytkownika
    najlepszy = kandydaci[1]
    wybrany_klucz = najlepszy[1]
    dane_odszyfrowane = najlepszy[2]
    
    os.makedirs("generated", exist_ok=True)
    sciezka_wyjsciowa = "generated\\cezar.txt"
    
    # Zapis odszyfrowanego tekstu
    with open(sciezka_wyjsciowa, "w", encoding="utf-8", errors="replace") as out_file:
        out_file.write(dane_odszyfrowane.decode("utf-8", errors="replace"))
        
    print(f"\n[SUKCES] Zapisano pełny odszyfrowany tekst dla klucza k={wybrany_klucz} do pliku: {sciezka_wyjsciowa}")

if __name__ == "__main__":
    analizuj_szyfr_cezara()
