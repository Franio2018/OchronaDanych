import hashlib
import os
import sys


def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).digest()


def sha256_file_chunks(path, chunk_size=4096):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.digest()


def check_sums(sums_path):
    # Ścieżki w pliku sum są względne wobec jego katalogu
    base_dir = os.path.dirname(sums_path)
    with open(sums_path, "rb") as f:
        lines = f.read().split(b"\n")

    for line in lines:
        if not line.strip():
            continue
        expected_hex, rel_path = line.decode("utf-8").split("  ", 1)
        path = os.path.join(base_dir, rel_path)
        try:
            actual = sha256_file(path)
        except FileNotFoundError:
            status = "BRAK"
        else:
            status = "OK" if actual == bytes.fromhex(expected_hex) else "BŁĄD"
        print(f"{rel_path}: {status}")


def bit_difference(a, b):
    return sum(bin(x ^ y).count("1") for x, y in zip(a, b))


if __name__ == "__main__":
    sums_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join("pliki-dla-studentow", "SHA256SUMS.txt")

    print(f"Sprawdzanie {sums_path}:")
    check_sums(sums_path)

    h1 = hashlib.sha256(b"Ala ma kota.").digest()
    h2 = hashlib.sha256(b"Ola ma kota.").digest()
    print("\nEfekt lawinowy:")
    print(f"  SHA-256('Ala ma kota.') = {h1.hex()}")
    print(f"  SHA-256('Ola ma kota.') = {h2.hex()}")
    print(f"  różniące się bity: {bit_difference(h1, h2)} / 256")

    # Dodatkowo: liczenie w kawałkach po 4096 B
    dane = os.path.join(os.path.dirname(sums_path), "dokumenty", "dane.bin")
    whole = sha256_file(dane)
    chunked = sha256_file_chunks(dane)
    print("\nDodatkowo — dane.bin w kawałkach po 4096 B:")
    print(f"  naraz:     {whole.hex()}")
    print(f"  kawałkami: {chunked.hex()}")
    print(f"  zgodne: {whole == chunked}")
