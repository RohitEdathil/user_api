
from re import compile, fullmatch
import random
import string
ph_regex = compile(r'(^[+0-9]{1,3})*([0-9]{10,11}$)')
email_regex = compile(
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')


def is_phone_number(num: str) -> bool:
    """
    Returns True if the given string is a valid phone number.
    """
    if fullmatch(ph_regex, num):
        return True
    return False


def is_email(email: str) -> bool:
    """
    Returns True if the given string is a valid email address.
    """
    if fullmatch(email_regex, email):
        return True
    return False


def generate_invite_code() -> str:
    """
    Generates a random invite code.
    """
    return ''.join(random.choice(string.ascii_uppercase + string.digits)
                   for _ in range(6))
