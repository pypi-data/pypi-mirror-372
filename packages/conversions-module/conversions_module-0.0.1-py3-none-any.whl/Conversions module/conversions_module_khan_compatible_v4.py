
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


def string_to_binary(text):
    """Converts a string to a space-separated binary string (e.g. 'Hi' → '01001000 01101001')."""
    return ' '.join(f'{ord(char):08b}' for char in text)


def binary_to_string(binary_str):
    """Converts a space-separated binary string (e.g. '01001000 01101001') back to ASCII text."""
    return ''.join(chr(int(b, 2)) for b in binary_str.split())

def toggle_string_binary(value):
    """
    Detects whether input is text or binary and converts accordingly.
    - If input is space-separated binary (e.g. '01001000 01101001'), it decodes to text.
    - Otherwise, it encodes text to binary.
    """
    try:
        if all(set(chunk) <= {'0', '1'} and len(chunk) == 8 for chunk in value.split()):
            return ''.join(chr(int(b, 2)) for b in value.split())
        else:
            return ' '.join(f'{ord(char):08b}' for char in value)
    except Exception:
        return "Invalid input"


# Store designation outputs here
_designation_store = {}

class DesignationError(Exception):
    """Raised when a requested designation does not exist or is invalid."""
    pass

def toggle_string_binary(value, save_with_designation=False, designation=None):
    """
    Converts between string and binary, with optional saving using a designation key.

    Parameters:
    - value: str - the input string or binary
    - save_with_designation: bool - whether to save the result with a name
    - designation: str - the name to save the result under (required if save_with_designation is True)

    Returns:
    - str - the toggled result
    """
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
    """
    Retrieves a saved result by designation and toggles it again.

    Parameters:
    - deseg: str - the name of the saved designation to toggle

    Returns:
    - str - the toggled result of the designated content

    Raises:
    - DesignationError if no designations exist or the name is invalid
    """
    if not _designation_store:
        raise DesignationError("no designations exist")
    if deseg not in _designation_store:
        raise DesignationError("invalid designation")
    return toggle_string_binary(_designation_store[deseg])
