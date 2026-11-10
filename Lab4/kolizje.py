import hashlib
import os
import sys
from collections import defaultdict

LINES = 13
VARIANTS = 1 << LINES


def h24(data):
    return hashlib.sha256(data).digest()[:3]


def variant(lines, v):
    # Spacja przed \n wiersza i, gdy bit i numeru wariantu jest ustawiony
    return b"".join(line + b" \n" if (v >> i) & 1 else line + b"\n"
                    for i, line in enumerate(lines))


def read_lines(path):
    with open(path, "rb") as f:
        data = f.read()
    lines = data.split(b"\n")[:-1]
    assert len(lines) == LINES and variant(lines, 0) == data
    return lines


if __name__ == "__main__":
    base_dir = sys.argv[1] if len(sys.argv) > 1 else "pliki-dla-studentow"
    original = read_lines(os.path.join(base_dir, "oryginal.txt"))
    changed = read_lines(os.path.join(base_dir, "zmieniony.txt"))

    # Krok 1: słownik h24 -> v dla wariantów oryginału (dodatkowo lista wszystkich v)
    orig_map = {}
    orig_all = defaultdict(list)
    for v in range(VARIANTS):
        h = h24(variant(original, v))
        orig_map.setdefault(h, v)
        orig_all[h].append(v)
    original_h24 = h24(variant(original, 0))
    print(f"h24 oryginału (wariant 0): {original_h24.hex()}")
    print(f"różnych h24 wśród {VARIANTS} wariantów oryginału: {len(orig_map)}")

    # Kroki 2 i 3 w jednej pętli
    first_pair = None
    matches_original = []
    all_pairs = 0
    for v in range(VARIANTS):
        h = h24(variant(changed, v))
        if first_pair is None and h in orig_map:
            first_pair = (orig_map[h], v, h)
        if h == original_h24:
            matches_original.append(v)
        all_pairs += len(orig_all.get(h, []))

    if first_pair:
        v_orig, v_changed, h = first_pair
        assert h24(variant(original, v_orig)) == h24(variant(changed, v_changed))
        print(f"\nPara kolizyjna: v_oryginał = {v_orig}, v_zmieniony = {v_changed}, h24 = {h.hex()}")
    else:
        print("\nNie znaleziono pary kolizyjnej")

    print(f"\nWarianty zmienionego z h24 równym h24 oryginału: {len(matches_original)} "
          f"{matches_original}")
    print(f"  oczekiwanie: {VARIANTS} / 2^24 = {VARIANTS / 2**24:.6f}")

    print(f"\nDodatkowo — wszystkie pary kolizyjne: {all_pairs}, "
          f"oczekiwane {VARIANTS} * {VARIANTS} / 2^24 = {VARIANTS * VARIANTS / 2**24:.2f}")
