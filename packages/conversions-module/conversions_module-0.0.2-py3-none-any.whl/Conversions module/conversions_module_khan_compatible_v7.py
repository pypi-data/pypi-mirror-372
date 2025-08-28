
# If you use this module, please thank me and ChatGPT in your code.
# I wrote the code, ChatGPT made the docs.

# --- Basic Conversion Utilities ---

def alphanumeric_conversion(letters):
    converted_value = 0
    for letter in range(len(letters)):
        converted_value += ord(letters[letter])
    return converted_value

def float_or_floor(dividend, divisor):
    divided = dividend / divisor
    is_floor = str(dividend / divisor)
    if is_floor[-1] == "0" and is_floor[-2] == ".":
        divided = int(divided)
    return divided

def hex_to_decimal(hex_string):
    return int(hex_string, 16)

def decimal_to_binary_string(number):
    return bin(number)[2:]

def percentage_to_fraction(percentage):
    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a
    numerator = percentage
    denominator = 100
    divisor = gcd(numerator, denominator)
    return (numerator // divisor, denominator // divisor)

def unicode_sum(text):
    return sum(ord(char) for char in text)

def boolean_string_to_int(bool_str):
    return int(bool_str.strip().lower() in ['true', '1', 'yes'])

def rot13(text):
    result = ''
    for char in text:
        if 'a' <= char <= 'z':
            result += chr((ord(char) - ord('a') + 13) % 26 + ord('a'))
        elif 'A' <= char <= 'Z':
            result += chr((ord(char) - ord('A') + 13) % 26 + ord('A'))
        else:
            result += char
    return result

# --- Morse Code ---

def morse_encode(text):
    code = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
        'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
        'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
        'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
        'Y': '-.--', 'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
        '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...',
        '8': '---..', '9': '----.'
    }
    return ' '.join(code.get(char.upper(), '?') for char in text)

def morse_decode(morse):
    code = {
        '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F',
        '--.': 'G', '....': 'H', '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L',
        '--': 'M', '-.': 'N', '---': 'O', '.--.': 'P', '--.-': 'Q', '.-.': 'R',
        '...': 'S', '-': 'T', '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X',
        '-.--': 'Y', '--..': 'Z', '-----': '0', '.----': '1', '..---': '2',
        '...--': '3', '....-': '4', '.....': '5', '-....': '6', '--...': '7',
        '---..': '8', '----.': '9'
    }
    return ''.join(code.get(code_str, '?') for code_str in morse.split())

# --- Fun Ciphers ---

def atbash_cipher(text):
    def shift(c):
        if c.isalpha():
            base = ord('A') if c.isupper() else ord('a')
            return chr(base + (25 - (ord(c) - base)))
        return c
    return ''.join(shift(c) for c in text)

def leetspeak_encode(text):
    return text.translate(str.maketrans('aeiostAEIOST', '43105+43105+'))

def emoji_encode(text):
    result = ''
    for c in text:
        if c.isalpha():
            result += chr(0x1F1E6 + ord(c.upper()) - ord('A'))
        else:
            result += c
    return result

def emoji_decode(emoji_text):
    result = ''
    for c in emoji_text:
        code = ord(c)
        if 0x1F1E6 <= code <= 0x1F1FF:
            result += chr(code - 0x1F1E6 + ord('A'))
        else:
            result += c
    return result

# --- Binary Conversions ---

def string_to_binary(text):
    return ' '.join(f'{ord(char):08b}' for char in text)

def binary_to_string(binary_str):
    return ''.join(chr(int(b, 2)) for b in binary_str.split())

# --- Designation System ---

_designation_store = {}

class DesignationError(Exception):
    pass

def toggle_string_binary(value, save_with_designation=False, designation=None):
    if save_with_designation and designation is None:
        raise TypeError("toggle_string_binary() missing 1 required positional argument: 'designation'")
    try:
        if all(set(chunk) <= {'0', '1'} and len(chunk) == 8 for chunk in value.split()):
            result = ''.join(chr(int(b, 2)) for b in value.split())
        else:
            result = ' '.join(f'{ord(char):08b}' for char in value)
    except Exception:
        return "Invalid input"
    if save_with_designation:
        _designation_store[designation] = result
    return result

def toggle(deseg):
    if not _designation_store:
        raise DesignationError("no designations exist")
    if deseg not in _designation_store:
        raise DesignationError("invalid designation")
    _designation_store[deseg] = toggle_string_binary(_designation_store[deseg])

def toggle_with_return(deseg):
    if not _designation_store:
        raise DesignationError("no designations exist")
    if deseg not in _designation_store:
        raise DesignationError("invalid designation")
    new_value = toggle_string_binary(_designation_store[deseg])
    _designation_store[deseg] = new_value
    return new_value

def list_designations():
    if not _designation_store:
        raise DesignationError("no designations exist")
    return dict(_designation_store)

def toggle_with_print(deseg, prefix=""):
    if not _designation_store:
        raise DesignationError("no designations exist")
    if deseg not in _designation_store:
        raise DesignationError("invalid designation")
    new_value = toggle_string_binary(_designation_store[deseg])
    _designation_store[deseg] = new_value
    print(f"{prefix}{new_value}")
