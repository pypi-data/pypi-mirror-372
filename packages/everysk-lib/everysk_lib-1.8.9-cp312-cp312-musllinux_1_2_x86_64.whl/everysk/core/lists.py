###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from math import ceil
from operator import itemgetter


###############################################################################
#   Public Functions Implementation
###############################################################################
def split_in_slices(total_size: int, slice_size: int) -> list[slice]:
    """
    Divides a range of a given size into slices of approximately equal lengths.

    Args:
        total_size (int): The total size of the range to be divided.
        slice_size (int): The desired size for each slice.

    Returns:
        list[slice]: A list of `slice` objects, where each slice represents a segment of the range. The slices cover the entire range without overlap.

    Examples:
        >>> split_in_slices(1, 2)
        [slice(0, 1)]
        >>> split_in_slices(3, 2)
        [slice(0, 2), slice(2, 3)]
        >>> split_in_slices(5, 3)
        [slice(0, 2), slice(2, 4), slice(4, 5)]
    """
    # Return an empty list if total_size or slice_size is invalid
    if total_size <= 0 or slice_size <= 0:
        return []

    # If the total_size is smaller than or equal to the desired slice size,
    # return a single slice that covers the entire range
    if total_size <= slice_size:
        return [slice(0, total_size)]

    # Calculate the number of slices needed
    n = int(ceil(total_size / float(slice_size)))

    # Compute the base slice size and the remainder
    k, m = divmod(total_size, n)

    # Generate slices using a list comprehension
    return [slice(i * k + min(i, m), (i + 1) * k + min(i + 1, m)) for i in range(n)]

def slices(lst: list, size: int) -> list:
    """
    Split the list in slices.
    https://stackoverflow.com/a/312464

    Args:
        lst (list): The list to split.
        size (int): The size of each slice.

    Returns:
        list: A list in which each element is a slice of the original list.

    Example:
        >>> from everysk.core.lists import slices
        >>> slices([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 2)
        [[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]]

    """
    return [lst[i:i + size] for i in range(0, len(lst), size)]

def sort_list_dict(*keys: list[str], lst: list[dict], reverse: bool = False) -> list:
    """
    Order a list of dictionaries by a specific key or keys.
    https://stackoverflow.com/a/73050

    Args:
        keys (list[str]): The key or keys to sort by.
        lst (list[dict]): The list of dictionaries to sort.
        reverse (bool): Whether to sort in reverse order.

    Returns:
        list: The sorted list of dictionaries.

    Example:
        >>> from everysk.core.lists import sort_list_dict
        >>> sort_list_dict('name', 'age', lst=[{'name': 'John', 'age': 25}, {'name': 'Jane', 'age': 22}], reverse=True)
        [{'name': 'John', 'age': 25}, {'name': 'Jane', 'age': 22}]
    """
    return sorted(lst, key=itemgetter(*keys), reverse=reverse)
