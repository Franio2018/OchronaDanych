import os
import sys
import math
from collections import Counter
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789"
SAMPLE_SIZE = 4096


def aes_ecb_decrypt(key, data):
    decryptor = Cipher(algorithms.AES(key), modes.ECB()).decryptor()
    return decryptor.update(data) + decryptor.finalize()


def calculate_entropy(data):
    # Liczone po surowych bajtach; bajty o liczności zero nie występują w Counter
    length = len(data)
    return -sum((count / length) * math.log2(count / length)
                for count in Counter(data).values())


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join("zadanie 3", "slaby_ecb.bin")
    with open(path, "rb") as f:
        ciphertext = f.read()

    sample = ciphertext[:SAMPLE_SIZE]
    results = []
    for char in ALPHABET:
        key = (char * 16).encode("ascii")
        # Próbka bez usuwania dopełnienia
        results.append((calculate_entropy(aes_ecb_decrypt(key, sample)), char))

    results.sort()
    print(f"Sprawdzono {len(results)} kluczy, próbka {len(sample)} B")
    print("Top 5 kandydatów (rosnąco wg H):")
    for place, (entropy, char) in enumerate(results[:5], start=1):
        print(f"  {place}. '{char}'  H = {entropy:.4f}")

    best_char = results[0][1]
    best_key = (best_char * 16).encode("ascii")
    padded = aes_ecb_decrypt(best_key, ciphertext)
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    plaintext = unpadder.update(padded) + unpadder.finalize()

    os.makedirs("generated", exist_ok=True)
    output_path = os.path.join("generated", "slaby_ecb.txt")
    with open(output_path, "wb") as f:
        f.write(plaintext)

    printable = set(range(32, 127)) | {9, 10, 13}
    printable_ratio = sum(1 for b in plaintext if b in printable) / len(plaintext)

    print(f"\nWybrany klucz: '{best_char}' x 16")
    print(f"Długość tekstu po usunięciu PKCS#7: {len(plaintext)} B")
    print(f"Udział znaków drukowalnych: {printable_ratio:.2%}")
    print(f"Pierwszy wiersz: {plaintext.decode('utf-8', errors='replace').splitlines()[0]}")
    print(f"Zapisano: {output_path}")
