###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from typing import Any


###############################################################################
#   Public Functions Implementation
###############################################################################
def is_float_convertible(value: Any) -> bool:
    """
    Check if a value can be successfully converted to a floating-point number.

    Args:
        value: The value to check for float convertibility.

    Returns:
        bool: True if the value can be converted to a float, False otherwise.

    Example:
        >>> is_float_convertible("3.14")
        True

        >>> is_float_convertible("not_a_number")
        False
    """
    try:
        float(value)
        return True
    except Exception: # pylint: disable=broad-exception-caught
        return False
