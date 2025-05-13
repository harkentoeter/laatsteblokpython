from cryptography.fernet import Fernet
from pathlib import Path

KEY_FILE = "secret.key"

def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as file:
        file.write(key)

def load_key():
    if not Path(KEY_FILE).exists():
        print("🔑 No key file found. Generating a new one...")
        generate_key()
    with open(KEY_FILE, "rb") as file:
        return file.read()

def encrypt_password(password: str, key: bytes) -> str:
    return Fernet(key).encrypt(password.encode()).decode()

def decrypt_password(token: str, key: bytes) -> str:
    return Fernet(key).decrypt(token.encode()).decode()

