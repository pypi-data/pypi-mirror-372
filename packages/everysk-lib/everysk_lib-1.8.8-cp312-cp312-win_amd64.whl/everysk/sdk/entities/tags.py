###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from types import NoneType
from typing import Any, Self
from collections.abc import Iterable

from six import string_types

from everysk.config import settings
from everysk.core.datetime import DateTime, Date
from everysk.core.exceptions import FieldValueError
from everysk.core.number import is_float_convertible
from everysk.core.string import normalize_string, to_string
from everysk.sdk.entities.base_list import EntityList


###############################################################################
#   Tags Class Implementation
###############################################################################
class Tags(EntityList):
    """
    A specialized list for handling tags.

    This class is a subclass of EntityList and provides specific validation for tags, including
    size limits and pattern matching.

    Attributes:
        min_size (int): The minimum allowed size for the list (default is 1).
        max_size (int): The maximum allowed size for the list (default is the value from settings).

    Example:
        To create a Tags for handling tags:
        tags = Tags()
    """
    min_size: int = 1
    max_size: int = settings.ENTITY_MAX_TAG_LENGTH

    def __init__(self, *args):
        """
        Initialize the Tags.

        Args:
            *args: Optional initial elements to populate the list.

        Example:
            To create an Tags with initial elements:
            >>> my_list = Tags(['tag1', 'tag2', 'tag3'])
        """
        if args:
            try:
                args = (list(dict.fromkeys(self.unify(args[0]))), )
            except TypeError:
                raise FieldValueError('Unsupported format in Tags.') from TypeError
        super().__init__(*args)

    def _validate(self, value: Any) -> str:
        """
        Validate a tag value.

        Args:
            value (str): The tag value to be validated.

        Raises:
            FieldValueError: If the tag value is invalid based on the specified criteria.

        Returns:
            str: The validated tag value.

        Criteria:
            - The value must be a string.
            - The value's length must be between min_size ({min_size}) and max_size ({max_size}).
            - The value must consist of only lowercase letters, digits, and underscores.
            - The value cannot be empty.

        Raises:
            FieldValueError: If the tag value does not meet the specified criteria.
        """
        if isinstance(value, list) or isinstance(value, dict):
            raise FieldValueError(f'Unsupported format in Tags: {type(value)}')
        elif value == '' or value is Undefined:
            value = str(None)
        elif is_float_convertible(value) or value.__class__ in [NoneType, bool]:
            value = str(value)
        elif value.__class__ in [DateTime, Date]:
            value = value.strftime('%Y%m%d')
        elif not isinstance(value, string_types):
            raise FieldValueError(f'Unsupported format in Tags: {type(value)}')

        value = to_string(''.join(x if x.isalnum() else '_' for x in normalize_string(value))).lower()

        if (
            self.min_size is not None and self.min_size > len(value) or
            self.max_size is not None and self.max_size < len(value)
        ):
            raise FieldValueError(f"Tags: '{value}' size it's not between {self.min_size} and {self.max_size}")

        return value

    def insert(self, __index: int, __object: Any) -> None:
        """
        Insert an object at a specified index if the object does not exist with validation.

        Args:
            __index (int): The index at which to insert the object.
            __object: The object to be inserted.
        """
        __object = self._validate(__object)
        if __object not in self:
            super().insert(__index, __object)

    def append(self, __object: Any) -> None:
        """
        Append an object to the list if the object does not exist with validation.

        Args:
            __object: The object to be appended.
        """
        __object = self._validate(__object)
        if __object not in self:
            super().append(__object)

    def extend(self, __iterable: Iterable) -> None:
        """
        Extend the list with values from an iterable if the value does not exist with validation.

        Args:
            __iterable (Iterable): An iterable containing values to be added to the list.
        """
        order_values: dict = {}
        for value in __iterable:
            value: str = self._validate(value)
            if value not in self:
                order_values[value] = None
        super().extend(list(order_values.keys()))

    @classmethod
    def unify(cls, tag_set: Any, reference_tags: list[Any] = None) -> Self:
        """
        Unify a set of tags with a reference set of tags.

        Args:
            tag_set (list): The set of tags to be unified.
            reference_tags (list): The reference set of tags.

        Returns:
            list: The unified set of tags.

        Example:
            To unify a set of tags with a reference set of tags:
            >>> unified_tags = Tags.unify_tags([['tag1', 'tag2'], ['tag3', 'tag4']], ['tag5', 'tag6'])
        """
        unified_tags: Self = cls()

        if not tag_set:
            return unified_tags
        elif isinstance(tag_set, (int, float)):
            tag_set = [tag_set]

        for tags in tag_set:
            if tags is not False and not tags and reference_tags:
                unified_tags.extend(reference_tags)
            elif isinstance(tags, list):
                unified_tags.extend(cls.unify(tags, reference_tags))
            else:
                unified_tags.append(tags)

        return unified_tags
