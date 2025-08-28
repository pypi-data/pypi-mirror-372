###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
import hmac

from everysk.config import settings
from everysk.core.exceptions import SigningError


SEPARATOR: bytes = b':'


###############################################################################
#   Public Functions Implementation
###############################################################################
def sign(data: str | bytes | bytearray, hash_name: str = 'sha1') -> bytes:
    """
    Sign the data with the SECRET_KEY.
    Possible hash algorithms are 'md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512'.

    Args:
        data (str | bytes | bytearray): The data to be signed.
        hash_name (str): The name of the hash algorithm to be used.
    """
    if isinstance(data, str):
        data = data.encode()

    digest = hmac.new(settings.EVERYSK_SIGNING_KEY.encode(), data, hash_name).hexdigest().encode()
    return SEPARATOR.join([digest, data])

def unsign(signed_data: bytes, hash_name: str = 'sha1') -> bytes | bytearray:
    """
    Unsign the data with the SECRET_KEY.
    Possible hash algorithms are 'md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512'.

    Args:
        signed_data (bytes): The signed data created by the sign method.
        hash_name (str): The name of the hash algorithm to be used.

    Raises:
        SigningError: If the signing key is invalid.
    """
    digest, data = signed_data.split(SEPARATOR, 1)
    if hmac.compare_digest(digest, hmac.new(settings.EVERYSK_SIGNING_KEY.encode(), data, hash_name).hexdigest().encode()):
        return data

    raise SigningError
