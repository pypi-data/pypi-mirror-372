###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
import string
import secrets
import uuid

from everysk.config import settings


ALPHANUMERIC = string.ascii_letters + string.digits
SYMBOL_ID_MAX_LEN = settings.SYMBOL_ID_MAX_LEN


###############################################################################
#   Public Functions Implementation
###############################################################################
def generate_random_id(length: int, characters: str = ALPHANUMERIC) -> str:
    """
    Generate a random ID based on the specified length and characters.

    Args:
        length (int): The desired length for the random ID.
        characters (str, optional): The characters to use for generating the ID.
            Default is alphanumeric characters.

    Returns:
        str: The generated random ID consisting of the specified characters.

    Example:
        >>> generate_random_id(18)
        'xiXwQuig6cI11ny095'

        >>> generate_random_id(5, 'abc')
        'cbacb'
    """
    return ''.join(secrets.choice(characters) for i in range(length))

def generate_unique_id():
    """
    Generate a unique ID with fixed length (32 characters).

    Returns:
        str: The generated unique ID consisting of hexadecimal characters.

    Example:
        >>> generate_unique_id()
        'dbdc803042ff48e19a344ad080a102dd'
    """
    return uuid.uuid4().hex

def generate_short_random_id() -> str:
    """
    Generate a random ID with a fixed length of 8 characters.

    Returns:
        str: The generated unique ID consisting of alphanumeric characters.

    Example:
        >>> generate_short_random_id()
        'u0tmNqHP'
    """
    return generate_random_id(length=settings.SIMPLE_UNIQUE_ID_LENGTH)
