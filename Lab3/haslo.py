import os
import sys
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ITERATIONS = 200_000
KEY_SIZE = 32
SALT_SIZE = 16
IV_SIZE = 16
PASSWORD = "Testowe-Haslo-2026"


def derive_key(password, salt):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=KEY_SIZE,
                     salt=salt, iterations=ITERATIONS)
    return kdf.derive(password.encode("utf-8"))


def encrypt(password, data):
    # Sól i IV losowane osobno, bezpiecznym generatorem
    salt = os.urandom(SALT_SIZE)
    iv = os.urandom(IV_SIZE)
    key = derive_key(password, salt)

    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded = padder.update(data) + padder.finalize()

    encryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()
    return salt, iv, ciphertext


def decrypt(password, salt, iv, ciphertext):
    key = derive_key(password, salt)

    decryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
    padded = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    return unpadder.update(padded) + unpadder.finalize()


def expected_length(data_length):
    # PKCS#7 zawsze dodaje od 1 do 16 bajtów
    return (data_length // 16 + 1) * 16


def run_test(name, data):
    salt, iv, ciphertext = encrypt(PASSWORD, data)
    recovered = decrypt(PASSWORD, salt, iv, ciphertext)
    same_bytes = recovered == data
    length_ok = len(ciphertext) == expected_length(len(data))
    status = "OK" if same_bytes and length_ok else "BŁĄD"
    print(f"Test '{name}': dane {len(data)} B, kryptogram {len(ciphertext)} B "
          f"(oczekiwano {expected_length(len(data))} B), "
          f"bajty zgodne: {same_bytes} -> {status}")
    return salt, iv, ciphertext


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join("zadanie 3", "wiadomosc.txt")
    with open(path, "rb") as f:
        message = f.read()

    print(f"Hasło testowe: {PASSWORD}")
    print(f"PBKDF2-HMAC-SHA256, {ITERATIONS} iteracji, klucz {KEY_SIZE} B, sól {SALT_SIZE} B\n")

    run_test("puste dane", b"")
    run_test("16 B ASCII", b"0123456789ABCDEF")
    salt1, iv1, ct1 = run_test("wiadomosc.txt", message)

    # Drugie szyfrowanie tej samej wiadomości tym samym hasłem
    salt2, iv2, ct2 = encrypt(PASSWORD, message)
    print("\nDwa szyfrowania wiadomosc.txt tym samym hasłem:")
    print(f"  sól 1: {salt1.hex()}  IV 1: {iv1.hex()}")
    print(f"  sól 2: {salt2.hex()}  IV 2: {iv2.hex()}")
    print(f"  kryptogram 1 (początek): {ct1[:32].hex()}")
    print(f"  kryptogram 2 (początek): {ct2[:32].hex()}")
    print(f"  kryptogramy równe: {ct1 == ct2}")
    print(f"  oba odszyfrowują się poprawnie: "
          f"{decrypt(PASSWORD, salt1, iv1, ct1) == decrypt(PASSWORD, salt2, iv2, ct2) == message}")
