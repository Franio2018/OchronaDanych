import time
import string
import itertools
from tqdm import tqdm
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

def rc4_ksa(key_bytes):
    S = list(range(256))
    j = 0
    key_length = len(key_bytes)
    for i in range(256):
        j = (j + S[i] + key_bytes[i % key_length]) % 256
        S[i], S[j] = S[j], S[i]
    return S

def rc4_prga(S, length):
    i = 0
    j = 0
    stream = bytearray(length)
    for n in range(length):
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        k = S[(S[i] + S[j]) % 256]
        stream[n] = k
    return stream

def rc4_crypt(key_bytes, data):
    S = rc4_ksa(key_bytes)
    stream = rc4_prga(S, len(data))
    return bytearray(b ^ s for b, s in zip(data, stream))

# Test odwracalności (dwukrotne zastosowanie)
def test_reversibility():
    test_key = b"abc"
    test_data = b"Hello, RC4!"
    encrypted = rc4_crypt(test_key, test_data)
    decrypted = rc4_crypt(test_key, encrypted)
    assert decrypted == test_data, "Błąd: Szyfr nie odtwarza wejścia!"
    print("Test odwracalności RC4: OK")

def calculate_entropy(data):
    if not data:
        return 0.0
    counter = Counter(data)
    length = len(data)
    return -sum((count / length) * math.log2(count / length) for count in counter.values())

def brute_force_rc4_visualized(filename):
    with open(filename, "rb") as f:
        ciphertext = f.read()

    start_time = time.time()
    results = []
    
    # Generowanie wszystkich 3-literowych kombinacji a-z
    alphabet = string.ascii_lowercase
    all_keys = [''.join(p) for p in itertools.product(alphabet, repeat=3)]
    
    # Przeszukiwanie z paskiem postępu tqdm
    for key_str in tqdm(all_keys, desc="Łamanie klucza RC4", unit="klucz"):
        key_bytes = key_str.encode('ascii')
        # Odszyfrowanie pierwszych 512 bajtów do analizy entropii
        sample_len = min(512, len(ciphertext))
        decrypted_sample = rc4_crypt(key_bytes, ciphertext[:sample_len])
        entropy = calculate_entropy(decrypted_sample)
        results.append((entropy, key_str))
        
    search_time = time.time() - start_time
    
    # Sortowanie rosnąco według entropii, przy remisie decyduje porządek alfabetyczny klucza
    results.sort(key=lambda x: (x[0], x[1]))
    
    # Automatyczny wybór pierwszego (najlepszego) kandydata
    best_entropy, best_key = results[0]
    best_key_bytes = best_key.encode('ascii')
    full_decrypted = rc4_crypt(best_key_bytes, ciphertext)
    
    # --- WIZUALIZACJA WYNIKÓW (Biblioteka Rich) ---
    
    # 1. Tabela z Top 5 kandydatów
    table = Table(title="Top 5 Kandydatów (Najniższa Entropia)", title_style="bold magenta")
    table.add_column("Miejsce", justify="center", style="cyan", no_wrap=True)
    table.add_column("Klucz", style="yellow", justify="center")
    table.add_column("Entropia", style="green", justify="right")
    
    for i in range(min(5, len(results))):
        ent, k_str = results[i]
        table.add_row(str(i + 1), k_str, f"{ent:.4f}")
        
    console.print("\n")
    console.print(table)
    
    # 2. Panel podsumowujący automatyczny wybór
    summary_content = (
        f"[bold green]Czas przeszukiwania:[/bold green] {search_time:.2f} s\n"
        f"[bold green]Przeanalizowano kluczy:[/bold green] {len(all_keys)}\n"
        f"[bold cyan]Automatycznie wybrany klucz:[/bold cyan] [yellow]{best_key}[/yellow]\n\n"
        f"[bold underline]Podgląd odszyfrowanego wiadomości:[/bold underline]\n"
        f"{full_decrypted[:150].decode('utf-8', errors='ignore')}..."
    )
    
    console.print(Panel(summary_content, title="[bold blue]Wynik Automatycznego Wyboru[/bold blue]", expand=False))
    
    return results, ciphertext, search_time, len(all_keys)

if __name__ == "__main__":
    test_reversibility()
    print(brute_force_rc4("zadanie\\rc4.bin"))
