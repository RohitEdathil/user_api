
from re import compile, fullmatch
from os import environ
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import random
import string

from sqlalchemy import exc
ph_regex = compile(r'(^[+0-9]{1,3})*([0-9]{10,11}$)')
email_regex = compile(
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

hasher = PasswordHasher()

try:
    SALT = environ['SALT']
except KeyError:
    print('SALT environment variable not set.')
    exit(1)


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


def generate_token() -> str:
    """
    Generates a random token.
    """
    return ''.join(random.choice(string.ascii_uppercase + string.digits)
                   for _ in range(16))


def hash_password(password: str) -> str:
    """
    Hashes the given password.
    Uses salt to prevent Rainbow table attacks.
    """
    return hasher.hash(password + SALT)


def check_password(password: str, hashed: str) -> bool:
    """
    Checks if the given password matches the hashed password.
    """
    try:
        return hasher.verify(hashed, password + SALT)
    except VerifyMismatchError:
        return False
