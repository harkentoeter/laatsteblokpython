import re
import hashlib
import base64
import random
import string
import unicodedata
import itertools
import math
import threading
import time
import psutil
import signal
import sys
from datetime import datetime
from itertools import permutations
from tqdm import tqdm

# Global control flags
RESOURCE_LIMIT_HIT = False
SHOULD_EXIT = False
PARTIAL_PASSWORDS = set()

MAX_CPU = 50.0
MAX_MEM = 50.0

def resource_monitor():
    global RESOURCE_LIMIT_HIT
    process = psutil.Process()
    while True:
        cpu = psutil.cpu_percent(interval=1)
        mem = process.memory_percent()
        RESOURCE_LIMIT_HIT = cpu > MAX_CPU or mem > MAX_MEM

def handle_exit(signum, frame):
    global SHOULD_EXIT
    SHOULD_EXIT = True
    print("\n[!] Graceful shutdown triggered. Saving progress...")
    write_to_file(list(PARTIAL_PASSWORDS), "partial_wordlist.txt")
    print("[✓] Partial wordlist saved to 'partial_wordlist.txt'. Exiting now.")
    sys.exit(0)

def normalize_text(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8').strip().lower()

def get_user_data():
    fields = [
        "First name", "Last name", "Nickname", "Birthdate (DDMMYYYY)",
        "Partner's name", "Partner's birthdate", "Pet name", "Favorite artist",
        "Favorite movie", "Favorite song", "Favorite food", "Postcode",
        "City of birth", "Country", "Phone number", "Username(s)",
        "Social media handle(s)", "Company or school", "Lucky number", "Favorite word",
        "Favorite band", "Child name", "Favorite number"
    ]
    data = {}
    for field in fields:
        key = re.sub(r'\W+', '', field).lower()
        data[key] = normalize_text(input(f"{field}: "))
    custom_keywords = []
    print("Enter custom keywords (one per line, leave blank to finish):")
    while True:
        word = input("Keyword: ").strip()
        if not word:
            break
        custom_keywords.append(normalize_text(word))
    data["customkeywords"] = custom_keywords
    return data

def extract_emails(file_path):
    email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        emails = set(email.lower() for email in re.findall(email_pattern, content))
        with open("found_emails.txt", "w") as f:
            for email in sorted(emails):
                f.write(email + "\n")
    except Exception:
        pass

def split_dob(dob):
    try:
        dt = datetime.strptime(dob, "%d%m%Y")
        return dt.strftime("%d"), dt.strftime("%m"), dt.strftime("%Y"), dt.strftime("%y"), dt.strftime("%Y")[::-1]
    except:
        return "01", "01", "1990", "90", "0991"

def predict_behavioral_password_patterns(data):
    return {
        f"{data['birthdateddmmyyyy'][-4:]} {data['favoritenumber']}",
        f"{data['birthdateddmmyyyy'][2:4]}{data['birthdateddmmyyyy'][:2]}{data['birthdateddmmyyyy'][-2:]}",
        f"{data['birthdateddmmyyyy'][:2]}{data['birthdateddmmyyyy'][2:4]}{data['birthdateddmmyyyy'][-2:]}",
        f"{data['favoriteband']} {data['favoritenumber']}",
        f"{data['childname']}{data['favoritenumber']}",
        f"{data['usernames']}_{data['favoritenumber']}",
        f"{data['usernames']}{data['birthdateddmmyyyy'][-2:]}",
        f"{data['usernames']}{data['childname']}{data['favoritenumber']}",
        f"{data['usernames']}!{data['favoritenumber']}",
        f"{data['usernames']}.{data['birthdateddmmyyyy'][2:4]}{data['birthdateddmmyyyy'][:2]}"
    }

def leet_variants(word):
    mappings = {'a': ['@', '4'], 'e': ['3'], 'i': ['1'], 'o': ['0'], 's': ['$', '5'], 't': ['7']}
    variants = {word}
    for i in range(len(word)):
        if word[i] in mappings:
            for repl in mappings[word[i]]:
                variants.add(word[:i] + repl + word[i+1:])
    return variants

def hash_variants(word):
    return {
        hashlib.md5(word.encode()).hexdigest()[:6],
        hashlib.sha1(word.encode()).hexdigest()[-8:],
        base64.b64encode(word.encode()).decode()[:10],
        str(sum(ord(c) for c in word)),
        str(sum(ord(c) for c in word) % 97),
        rot13(word),
        ''.join(hex(ord(c))[2:] for c in word)
    }

def rot13(s):
    result = []
    for c in s:
        if 'a' <= c <= 'z':
            result.append(chr((ord(c) - ord('a') + 13) % 26 + ord('a')))
        elif 'A' <= c <= 'Z':
            result.append(chr((ord(c) - ord('A') + 13) % 26 + ord('A')))
        else:
            result.append(c)
    return ''.join(result)

def generate_math_suffixes(word, dob, phone, lucky):
    try:
        day, month, year = map(int, dob.split('-')) if '-' in dob else (1, 1, 1990)
    except:
        day, month, year = 1, 1, 1990
    phone_digits = ''.join([c for c in phone if c.isdigit()]) or '1'
    ascii_ordinals = [ord(c) for c in word]
    sum_ascii = sum(ascii_ordinals)
    prod_ascii = math.prod(ascii_ordinals) if ascii_ordinals else 1
    mod_97 = sum_ascii % 97
    mod_phone = sum_ascii % int(phone_digits)
    mod_lucky = sum_ascii % int(lucky) if lucky.isdigit() else 1
    return {
        f'{word}_{sum_ascii}', f'{word}_{prod_ascii}', f'{word}_{mod_97}',
        f'{word}_{mod_phone}', f'{word}_{mod_lucky}', f'{sum_ascii}_{word}',
        f'{prod_ascii}_{word}', f'{mod_97}_{word}', f'{mod_phone}_{word}',
        f'{mod_lucky}_{word}'
    }

def phrase_permutation_combinator(words):
    combinations = set()
    for i in range(1, len(words) + 1):
        for subset in permutations(words, i):
            for sep in ['', '_', '.', '@', '-', '!']:
                combinations.add(sep.join(subset))
            combinations.add(''.join(word.capitalize() for word in subset))
    return combinations

def generate_variants(data):
    global PARTIAL_PASSWORDS
    if SHOULD_EXIT: return []
    day, month, year, year_suffix, reversed_year = split_dob(data.get("birthdateddmmyyyy", ""))
    phone = re.sub(r"\D", "", data.get("phonenumber", ""))
    lucky = data.get("luckynumber", "7")
    all_words = set()
    for v in data.values():
        if isinstance(v, str):
            all_words.update(v.split())
        elif isinstance(v, list):
            all_words.update(v)

    base_variants = set()
    for word in tqdm(all_words, desc="Generating base variants"):
        if SHOULD_EXIT: break
        word = word.lower()
        base_variants.update({word, word[::-1], word.title(), word.upper()})
        base_variants.update(leet_variants(word))
    PARTIAL_PASSWORDS.update(base_variants)

    if SHOULD_EXIT: return list(PARTIAL_PASSWORDS)

    math_variants = set()
    for word in base_variants:
        if SHOULD_EXIT: break
        math_variants.update(generate_math_suffixes(word, f"{day}-{month}-{year}", phone, lucky))
    PARTIAL_PASSWORDS.update(math_variants)

    if SHOULD_EXIT: return list(PARTIAL_PASSWORDS)

    combo_variants = set()
    symbols = ['_', '-', '.', '@', '!', '#']
    for b in base_variants:
        if SHOULD_EXIT: break
        combo_variants.update({b + s + e for s in symbols for e in [day, month, year, year_suffix, reversed_year, lucky, phone[-4:], phone[:3]]})
    PARTIAL_PASSWORDS.update(combo_variants)

    if SHOULD_EXIT: return list(PARTIAL_PASSWORDS)

    hashed = set()
    for w in base_variants:
        if SHOULD_EXIT: break
        hashed.update(hash_variants(w))
    PARTIAL_PASSWORDS.update(hashed)

    if SHOULD_EXIT: return list(PARTIAL_PASSWORDS)

    smart_phrases = phrase_permutation_combinator(list(all_words))
    PARTIAL_PASSWORDS.update(smart_phrases)

    randoms = {''.join(random.choices(string.ascii_letters + string.digits + '!@#$%^&*', k=10)) for _ in range(30)}
    PARTIAL_PASSWORDS.update(randoms)

    behavioral_variants = predict_behavioral_password_patterns(data)
    PARTIAL_PASSWORDS.update(behavioral_variants)

    final = set(w for w in PARTIAL_PASSWORDS if 6 <= len(w) <= 18)
    return sorted(final, key=lambda x: (-sum(not c.isalnum() for c in x), -len(x)))

def write_to_file(passwords, filename="wordlist.txt"):
    with open(filename, "w") as f:
        for pw in passwords:
            f.write(pw + "\n")

def main():
    signal.signal(signal.SIGINT, handle_exit)
    threading.Thread(target=resource_monitor, daemon=True).start()
    extract_emails("input.txt")
    data = get_user_data()
    passwords = generate_variants(data)
    output_file = "wordlist.txt"
    if not SHOULD_EXIT:
        write_to_file(passwords, output_file)
        print(f"\n[✓] Password list written to {output_file}")

if __name__ == "__main__":
    main()

