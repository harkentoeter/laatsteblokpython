import os
from encryption import encrypt_password, decrypt_password, load_key

MASTER_PASS_FILE = "master.pass"

def is_first_time():
    return not os.path.exists(MASTER_PASS_FILE)

def set_master_password(password):
    key = load_key()
    encrypted = encrypt_password(password, key)
    with open(MASTER_PASS_FILE, "wb") as f:
        f.write(encrypted)

def verify_master_password(input_password):
    key = load_key()
    try:
        with open(MASTER_PASS_FILE, "rb") as f:
            encrypted = f.read()
        decrypted = decrypt_password(encrypted, key)
        return decrypted == input_password
    except:
        return False

def reset_application():
    if os.path.exists(MASTER_PASS_FILE):
        os.remove(MASTER_PASS_FILE)
    if os.path.exists("passwords.json"):
        os.remove("passwords.json")
    print("\n[!] All data has been reset.")

