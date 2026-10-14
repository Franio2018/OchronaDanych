from hashlib import sha256

txts = ["Ala ma kota.", "Ala ma kota!"]
for txt in txts:
    hsh = sha256(txt.encode("utf-8")).hexdigest()
    print(txt)
    print(hsh) 