import hashlib
import hmac
import os
import secrets
import sys
import time

ITERATIONS = 600_000
SALT_SIZE = 16


def pbkdf2(password, salt, iterations):
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)


def load_db(path):
    db = {}
    with open(path, "rb") as f:
        for line in f.read().decode("utf-8").split("\n"):
            if not line.strip():
                continue
            login, iterations, salt_hex, hash_hex = line.split(":")
            db[login] = (int(iterations), bytes.fromhex(salt_hex), bytes.fromhex(hash_hex))
    return db


def weryfikuj(db, login, password):
    if login not in db:
        return False
    iterations, salt, stored = db[login]
    return hmac.compare_digest(pbkdf2(password, salt, iterations), stored)


def dodaj(db, login, password):
    salt = secrets.token_bytes(SALT_SIZE)
    db[login] = (ITERATIONS, salt, pbkdf2(password, salt, ITERATIONS))
    return f"{login}:{ITERATIONS}:{salt.hex()}:{db[login][2].hex()}"


def mean_time(iterations, calls):
    salt = secrets.token_bytes(SALT_SIZE)
    start = time.perf_counter()
    for _ in range(calls):
        pbkdf2("haslo", salt, iterations)
    return (time.perf_counter() - start) / calls


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join("pliki-dla-studentow", "hasla.txt")
    db = load_db(path)

    print("Weryfikacja:")
    tests = [
        ("anna", "Kasztan-2026", True),
        ("anna", "kasztan-2026", False),
        ("piotr", "Żółw na łące", True),
        ("kasia", "Kasztan-2026", False),
    ]
    for login, password, expected in tests:
        result = weryfikuj(db, login, password)
        status = "OK" if result == expected else "BŁĄD"
        print(f"  {login}, {password} -> {result} (oczekiwano {expected}) {status}")

    password = "Wspolne-Haslo-2026"
    dodaj(db, "test1", password)
    dodaj(db, "test2", password)
    _, salt1, hash1 = db["test1"]
    _, salt2, hash2 = db["test2"]
    print(f"\nNowe konta test1 i test2, to samo hasło, {ITERATIONS} iteracji:")
    print(f"  sól test1:   {salt1.hex()}")
    print(f"  sól test2:   {salt2.hex()}")
    print(f"  skrót test1: {hash1.hex()}")
    print(f"  skrót test2: {hash2.hex()}")
    print(f"  sole równe: {salt1 == salt2}, skróty równe: {hash1 == hash2}")
    print(f"  weryfikuj(test1): {weryfikuj(db, 'test1', password)}, "
          f"weryfikuj(test2): {weryfikuj(db, 'test2', password)}")

    # Dodatkowo: słabe rekordy i koszt przeszukania
    weak = [login for login, (iterations, _, _) in db.items() if iterations < ITERATIONS]
    print(f"\nDodatkowo — loginy z mniej niż {ITERATIONS} iteracji: {', '.join(weak)}")
    t1 = mean_time(1, 10_000)
    t600k = mean_time(ITERATIONS, 5)
    candidates = 26 ** 6
    print(f"  średni czas PBKDF2, 1 iteracja:      {t1 * 1e6:.2f} µs")
    print(f"  średni czas PBKDF2, {ITERATIONS} iteracji: {t600k * 1e3:.1f} ms")
    print(f"  26^6 = {candidates} haseł: 1 iteracja ≈ {candidates * t1 / 60:.1f} min, "
          f"{ITERATIONS} iteracji ≈ {candidates * t600k / 86400 / 365:.1f} lat")
