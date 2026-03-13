import hashlib

def make_key(computer_id):
    secret = "MERAWI2026PRO"
    combined = computer_id + secret
    key = hashlib.md5(combined.encode()).hexdigest()[:16].upper()
    return f"{key[:4]}-{key[4:8]}-{key[8:12]}-{key[12:16]}"

if __name__ == "__main__":
    print("Enter Computer ID:", end=" ")
    cid = input().strip()
    key = make_key(cid)
    print(f"\nLicense Key: {key}")