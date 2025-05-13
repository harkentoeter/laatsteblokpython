import os
import shutil
import time
from encryption import load_key, encrypt_password, decrypt_password
from password_generator import generate_chaotic_string, extract_random_password
from utils import load_data, save_data

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def prompt_input(prompt):
    return input(prompt + "\n>> ")

def generate_and_store():
    site = prompt_input("Enter Site Name:")
    username = prompt_input("Enter Username:")
    try:
        length = int(prompt_input("Enter Desired Password Length:"))
    except ValueError:
        print("Invalid length. Must be a number.")
        return

    chaotic = generate_chaotic_string(10000)
    password = extract_random_password(chaotic, length)

    key = load_key()
    encrypted_password = encrypt_password(password, key)

    data = load_data()
    data[site] = {"username": username, "password": encrypted_password}
    save_data(data)

    print(f"Password stored for '{site}'")
    print(f"Generated Password: {password}")

def retrieve_password():
    site = prompt_input("Enter Site Name:")
    data = load_data()
    if site not in data:
        print("Site not found.")
        return

    key = load_key()
    encrypted = data[site]["password"]
    decrypted = decrypt_password(encrypted, key)

    print(f"Username: {data[site]['username']}")
    print(f"Password: {decrypted}")

def view_all_passwords():
    data = load_data()
    key = load_key()
    for site, creds in data.items():
        decrypted = decrypt_password(creds["password"], key)
        print(f"{site} | {creds['username']} | {decrypted}")

def main():
    while True:
        print("Select an option:")
        print("[1] Generate New Password")
        print("[2] Retrieve Stored Password")
        print("[3] View All Stored Passwords")
        print("[4] Exit")

        choice = input(">> ").strip()

        if choice == "1":
            generate_and_store()
        elif choice == "2":
            retrieve_password()
        elif choice == "3":
            view_all_passwords()
        elif choice == "4":
            print("Exiting... Goodbye.")
            break
        else:
            print("Invalid option.")

        input("\n[ Press Enter to continue ]")

if __name__ == "__main__":
    main()

