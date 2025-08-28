
# If you use this module, please thank me and ChatGPT in your code.
# I wrote the code, ChatGPT made the docs.

def alphanumeric_conversion(letters):
    """Converts a string of letters to a numeric value by summing Unicode values."""
    converted_value = 0
    for letter in range(len(letters)):
        converted_value += ord(letters[letter])
    return converted_value

def float_or_floor(dividend, divisor):
    """Returns a float unless the result is a whole number, then returns as int."""
    divided = dividend / divisor
    is_floor = str(dividend / divisor)
    if is_floor[-1] == "0" and is_floor[-2] == ".":
        divided = int(divided)
    return divided

def hex_to_decimal(hex_string):
    """Converts a hexadecimal string (e.g. '1A3F') to a decimal integer."""
    return int(hex_string, 16)

def decimal_to_binary_string(number):
    """Converts an integer to a binary string (e.g. 5 -> '101')."""
    return bin(number)[2:]

def percentage_to_fraction(percentage):
    """Converts a percentage (e.g. 75) to a simplified fraction tuple (3, 4)."""
    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a
    numerator = percentage
    denominator = 100
    divisor = gcd(numerator, denominator)
    return (numerator // divisor, denominator // divisor)

def unicode_sum(text):
    """Returns the sum of all Unicode code points in a string."""
    return sum(ord(char) for char in text)

def boolean_string_to_int(bool_str):
    """Converts common boolean strings ('true', 'false') to integers (1 or 0)."""
    return int(bool_str.strip().lower() in ['true', '1', 'yes'])

def rot13(text):
    """Encodes or decodes text using ROT13 cipher (letters rotated by 13 positions)."""
    result = ''
    for char in text:
        if 'a' <= char <= 'z':
            result += chr((ord(char) - ord('a') + 13) % 26 + ord('a'))
        elif 'A' <= char <= 'Z':
            result += chr((ord(char) - ord('A') + 13) % 26 + ord('A'))
        else:
            result += char
    return result

def morse_encode(text):
    """Encodes a string into Morse code using spaces between letters."""
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
    """Decodes a Morse code string back into text."""
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

def atbash_cipher(text):
    """Encodes text using the Atbash cipher (reverses alphabet)."""
    def shift(c):
        if c.isalpha():
            base = ord('A') if c.isupper() else ord('a')
            return chr(base + (25 - (ord(c) - base)))
        return c
    return ''.join(shift(c) for c in text)

def binary_string_to_text(binary_str):
    """Converts a binary string (e.g. '01001000') to ASCII text."""
    chars = binary_str.split()
    return ''.join(chr(int(b, 2)) for b in chars)

def leetspeak_encode(text):
    """Encodes text into basic Leetspeak."""
    return text.translate(str.maketrans('aeiostAEIOST', '43105+43105+'))

def emoji_encode(text):
    """Encodes ASCII A-Z into emoji using regional indicators."""
    result = ''
    for c in text:
        if c.isalpha():
            result += chr(0x1F1E6 + ord(c.upper()) - ord('A'))
        else:
            result += c
    return result

def emoji_decode(emoji_text):
    """Decodes regional indicator emojis back to A-Z."""
    result = ''
    for c in emoji_text:
        code = ord(c)
        if 0x1F1E6 <= code <= 0x1F1FF:
            result += chr(code - 0x1F1E6 + ord('A'))
        else:
            result += c
    return result
