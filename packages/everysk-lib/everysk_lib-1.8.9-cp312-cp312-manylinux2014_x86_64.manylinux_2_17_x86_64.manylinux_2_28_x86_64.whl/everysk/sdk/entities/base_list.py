###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from collections.abc import Iterable
from typing import Any

from everysk.core.exceptions import FieldValueError


###############################################################################
#   EntityList Class Implementation
###############################################################################
class EntityList(list):
    """
    A list subclass with validation capabilities.

    This class extends the standard Python list and adds validation for the values
    added or inserted into it.

    Attributes:
        min_size (int): The minimum allowed size for the list (default is None).
        max_size (int): The maximum allowed size for the list (default is None).

    Example:
        To create a custom list with validation capabilities:
        my_list = EntityList()
    """
    min_size: int | None = None
    max_size: int | None = None

    def __init__(self, *args) -> None:
        """
        Initialize the EntityList.

        Args:
            *args: Optional initial elements to populate the list.

        Example:
            To create an EntityList with initial elements:
            my_list = EntityList([1, 2, 3])
        """
        if args:
            try:
                args = ([self._validate(item) for item in args[0]], )
            except TypeError:
                raise FieldValueError('Unsupported format.') from TypeError
        super().__init__(*args)

    def __setitem__(self, index: int, value: Any) -> None:
        """
        Set an item in the list with validation.

        Args:
            index (int): The index at which to set the value.
            value: The value to be set.
        """
        value = self._validate(value)
        return super().__setitem__(index, value)

    def insert(self, __index: int, __object: Any) -> None:
        """
        Insert an object at a specified index with validation.

        Args:
            __index (int): The index at which to insert the object.
            __object: The object to be inserted.
        """
        __object = self._validate(__object)
        return super().insert(__index, __object)

    def append(self, __object: Any) -> None:
        """
        Append an object to the list with validation.

        Args:
            __object: The object to be appended.
        """
        __object = self._validate(__object)
        return super().append(__object)

    def extend(self, __iterable: Iterable) -> None:
        """
        Extend the list with values from an iterable with validation.

        Args:
            __iterable (Iterable): An iterable containing values to be added to the list.
        """
        for value in __iterable:
            value = self._validate(value)
        return super().extend(__iterable)

    def _validate(self, value: Any) -> Any:
        """
        Validate a value.

        Args:
            value: The value to be validated.

        Raises:
            NotImplementedError: This method should be overridden in subclasses.

        Returns:
            The validated value.
        """
        raise NotImplementedError()

    def to_native(self, add_class_path: str | None = None, recursion: bool = False) -> Any:
        """
        Converts the object to the specified Python type.

        Args:
            add_class_path (str | None, optional): The class path to add when converting the object. Defaults to None.
            recursion (bool, optional): Indicates whether to recursively convert nested objects. Defaults to False.

        Returns:
            object: The converted object.

        """
        return self.to_list(add_class_path=add_class_path, recursion=recursion)

    def to_list(self, add_class_path: bool = False, recursion: bool = False) -> list[dict]: # pylint: disable=unused-argument
        """
        Convert the Securities collection to a list of dictionaries.
        """
        return list(self)
