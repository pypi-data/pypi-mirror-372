###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from typing import Any, Generator

###############################################################################
#   Public functions Implementation
###############################################################################
def bool_convert(value: Any) -> bool:
    """
    Convert any of these to True: 'y', 'yes', 'true', 'on', '1'
    Convert any of these to Fale: 'n', 'no', 'false', 'off', '0'

    Args:
        value (Any): The value to be converted to a boolean

    Returns:
        Boolean: indicating if the value is either True or False

    Raises:
        ValueError: if value is none of these presented above.

    Example:
        >>> from everysk.utils import bool_convert
        >>> bool_convert('y')
        >>> True

        >>> bool_convert('n')
        >>> False

        >>> bool_convert('a')
        >>> ValueError: Invalid truth value 'a'
    """
    value = str(value).lower()
    if value in ('y', 'yes', 'true', 'on', '1'):
        value = True
    elif value in ('n', 'no', 'false', 'off', '0'):
        value = False
    else:
        raise ValueError(f"Invalid truth value '{value}'.")

    return value

def search_key_on_dict(search_key: str, value: Any) -> Generator:
    """
    Search for key recursive on value.
    The first value need to be a dict for this function work properly.

    Args:
        search_key (str): The key that must be found.
        value (Any): The item where the key must be found.

    Yields:
        Generator: The generator with all corresponding values found by the key.

    Example:
        >>> from everysk.utils import search_key_on_dict
        >>> data = {
        >>> ... "name" : "John Doe",
        >>> ... "age" : 32
        >>> }
        >>> search_key_on_dict("name", data)
        >>> John Doe
    """
    if hasattr(value, 'items'):
        for key, val in value.items():
            if key == search_key:
                yield val
            if isinstance(val, dict):
                for result in search_key_on_dict(search_key, val):
                    yield result
            elif isinstance(val, list):
                for item in val:
                    for result in search_key_on_dict(search_key, item):
                        yield result
