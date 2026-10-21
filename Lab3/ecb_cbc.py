import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

BLOCK_SIZE = 16


def aes_encrypt(key, mode, data):
    encryptor = Cipher(algorithms.AES(key), mode).encryptor()
    return encryptor.update(data) + encryptor.finalize()


def aes_decrypt(key, mode, data):
    decryptor = Cipher(algorithms.AES(key), mode).decryptor()
    return decryptor.update(data) + decryptor.finalize()


def split_blocks(data):
    return [data[i:i + BLOCK_SIZE] for i in range(0, len(data), BLOCK_SIZE)]


def equal_blocks(blocks):
    # Pary indeksów (od 1) bloków o identycznej zawartości
    return [(i + 1, j + 1)
            for i in range(len(blocks))
            for j in range(i + 1, len(blocks))
            if blocks[i] == blocks[j]]


def print_ciphertext(name, ciphertext):
    blocks = split_blocks(ciphertext)
    print(f"{name} ({len(ciphertext)} B):")
    for n, block in enumerate(blocks, start=1):
        print(f"  blok {n}: {block.hex()}")
    pairs = equal_blocks(blocks)
    print(f"  równe bloki: {pairs if pairs else 'brak'}")


if __name__ == "__main__":
    plaintext = b"0123456789ABCDEF" * 4
    # Klucz podany szesnastkowo -> 16 bajtów, nie 32 znaki tekstu
    key = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
    iv = os.urandom(BLOCK_SIZE)

    # Brak paddera: dane mają 64 B, czyli wielokrotność bloku
    ecb = aes_encrypt(key, modes.ECB(), plaintext)
    cbc = aes_encrypt(key, modes.CBC(iv), plaintext)

    print(f"Tekst jawny ({len(plaintext)} B): {plaintext.decode('ascii')}")
    print(f"Klucz: {key.hex()}")
    print(f"IV:    {iv.hex()}\n")
    print_ciphertext("ECB", ecb)
    print_ciphertext("CBC", cbc)

    ecb_ok = aes_decrypt(key, modes.ECB(), ecb) == plaintext
    cbc_ok = aes_decrypt(key, modes.CBC(iv), cbc) == plaintext
    print(f"\nOdszyfrowanie ECB == wejście: {'OK' if ecb_ok else 'BŁĄD'}")
    print(f"Odszyfrowanie CBC == wejście: {'OK' if cbc_ok else 'BŁĄD'}")
