import random

# === Chaos Character Generators ===

def generate_random_letter():
    letter = chr(random.randint(97, 122))
    for _ in range(5):
        op = random.choice(["+", "-"])
        operand = random.randint(0, 10)
        if op == "+":
            letter = chr((ord(letter) + operand) % 126)
        else:
            letter = chr((ord(letter) - operand) % 126)
    return letter

def generate_random_digit():
    digit = random.randint(0, 9)
    for _ in range(5):
        op = random.choice(["+", "-"])
        operand = random.randint(0, 5)
        if op == "+":
            digit = (digit + operand) % 10
        else:
            digit = (digit - operand) % 10
    return str(digit)

def generate_random_punctuation():
    punct = random.choice("!@#$%^&*()_+-=[]{}|;':\"<>,./?`~")
    for _ in range(5):
        op = random.choice(["+", "-"])
        operand = random.randint(0, 5)
        punct = chr((ord(punct) + operand) % 126) if op == "+" else chr((ord(punct) - operand) % 126)
    return punct

# === Hustles 1–10 (assumed already present) ===

def hustle1(password):
    p = list(password)
    random.shuffle(p)
    return "".join(p)

def hustle2(password):
    for _ in range(random.randint(1, 5)):
        char = random.choice("!@#$%^&*()_+-=")
        password = char + password + char
    return password

def hustle3(password):
    num_replacements = len(password) // 2
    password = list(password)
    for _ in range(num_replacements):
        i = random.randint(0, len(password) - 1)
        password[i] = random.choice("!@#$%^&*()_+-=")
    return "".join(password)

def hustle4(password):
    for _ in range(random.randint(1, 5)):
        i = random.randint(0, len(password) - 1)
        digit = str(random.randint(0, 9))
        password = password[:i] + digit + password[i:]
    return password

def hustle5(password):
    mashed = ""
    for c in password:
        mashed += c if random.randint(0, 1) == 0 else str(random.randint(0, 9))
    return mashed

def hustle6(password):
    return password[::-1]

def hustle7(password):
    result = ""
    for c in password:
        if c.isalpha():
            result += chr((ord(c) + 1) % 126)
        else:
            result += c
    return result

def hustle8(password):
    return "".join(c.upper() if random.random() < 0.5 else c.lower() for c in password)

def hustle9(password):
    return password + password[::-1]

def hustle10(password):
    return "".join(random.choice([c, "*", "%", "#", "!"]) for c in password)

# === New Hustles 11–13 ===

def hustle11(password):
    password = list(password)
    for _ in range(len(password) // 4):
        i = random.randint(0, len(password) - 1)
        password[i] = generate_random_letter()
    return "".join(password)

def hustle12(password):
    for _ in range(len(password) // 6):
        i = random.randint(0, len(password))
        password = password[:i] + generate_random_digit() + password[i:]
    return password

def hustle13(password):
    password = list(password)
    for _ in range(len(password) // 5):
        i = random.randint(0, len(password) - 1)
        password[i] = generate_random_punctuation()
    return "".join(password)

# === Hustle Pool ===

hustles = [
    hustle1, hustle2, hustle3, hustle4, hustle5,
    hustle6, hustle7, hustle8, hustle9, hustle10,
    hustle11, hustle12, hustle13
]

# === Final Program Logic ===

def generate_chaotic_string(length):
    charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;':\"<>,./?`~"
    base = "".join(random.choice(charset) for _ in range(length))
    for _ in range(random.randint(10, 20)):
        hustle = random.choice(hustles)
        base = hustle(base)
    return base

def extract_random_password(base_output, desired_length):
    if len(base_output) < desired_length:
        raise ValueError("Base output is shorter than desired password length.")
    start = random.randint(0, len(base_output) - desired_length)
    return base_output[start:start + desired_length]

# === Main ===

def main():
    try:
        max_length = 1000000
        requested_length = int(input("Enter desired password length: "))
        if requested_length <= 0 or requested_length > max_length:
            raise ValueError("Password length must be between 1 and 10000.")

        print("\nGenerating chaotic base output...\n")
        chaotic_output = generate_chaotic_string(max_length)

        final_password = extract_random_password(chaotic_output, requested_length)

        print("\n\nYour final password:\n")
        print(final_password)

    except ValueError as ve:
        print(f"Error: {ve}")

if __name__ == "__main__":
    main()

