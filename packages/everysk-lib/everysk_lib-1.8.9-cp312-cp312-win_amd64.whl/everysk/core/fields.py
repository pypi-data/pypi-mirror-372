###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
import re
from collections.abc import Callable, Iterator
from sys import maxsize as max_int
from types import UnionType
from typing import Any
from urllib.parse import urlparse

from everysk.core.datetime import Date, DateTime
from everysk.core.exceptions import FieldValueError, ReadonlyError
from everysk.core.object import BaseDict, BaseField
from everysk.utils import bool_convert


###############################################################################
#   Private Functions Implementation
###############################################################################
def _do_nothing(*args, **kwargs) -> None:
    # pylint: disable=unused-argument
    raise ReadonlyError('This field value cannot be changed.')


def _min_max_validate(min_value: Any, max_value: Any, value: Any, attr_name: str) -> None:
    """
    Helper function to validate if value is between min and max for fields.

    Args:
        min_value (Any): The min value to be checked.
        max_value (Any): The max value to be checked.
        value (Any): The value used to validate.
        attr_name (str): The name of the attribute to be used on errors.

    Raises:
        FieldValueError: If the value is not between min and max.

    Example:
        >>> _min_max_validate(0, 10, 5, "my_field")
        # No exception is raised

        >>> _min_max_validate(0, 10, 15, "my_field")
        # FieldValueError is raised with the message:
        # "The value '15' for field 'my_field' must be between 0 and 10."
    """
    if value is not None and value is not Undefined:
        min_check = False
        max_check = False

        # Check if min_value and max_value are callable
        min_value = min_value if not callable(min_value) else min_value()
        max_value = max_value if not callable(max_value) else max_value()

        if min_value is not None and min_value is not Undefined:
            min_check = value < min_value

        if max_value is not None and max_value is not Undefined:
            max_check = value > max_value

        if min_check or max_check:
            msg = f"The value '{value}' for field '{attr_name}' must be between {min_value} and {max_value}."
            raise FieldValueError(msg)


###############################################################################
#   Field Class Implementation
###############################################################################
class Field(BaseField):
    attr_type: Any = Any
    choices: set = None

    def __new__(cls, *args, **kwargs) -> Any:
        """
        For the VSCode autocomplete works correctly, we need to say what is the
        type that the method __new__ returns
        """
        return super().__new__(cls)

    def __init__(
        self,
        default: Any = None,
        *,
        required: bool = False,
        readonly: bool = False,
        required_lazy: bool = False,
        empty_is_none: bool = False,
        choices: set | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            attr_type=self.attr_type,
            default=default,
            required=required,
            readonly=readonly,
            required_lazy=required_lazy,
            empty_is_none=empty_is_none,
            choices=choices,
            **kwargs,
        )
        if self.default not in (None, Undefined) and self._has_invalid_choices(self.default):
            msg = f"The default value '{self.default}' must be in this list {self.choices}."
            raise FieldValueError(msg)

    def _get_choices(self) -> set:
        """Returns the list of choices."""
        return self.choices or set()

    def _has_invalid_choices(self, value: Any) -> bool:
        """
        Validates whether the given value is within the allowed choices.

        If `self.attr_type` is a list, tuple, or set, it checks whether all elements in `value`
        exist in `self.choices`. If `value` is a single item, it verifies its presence in `self.choices`.

        Args:
            value (Any): The value or collection of values to validate.

        Returns:
            bool: True if the value is invalid (not in `self.choices`), otherwise False.
        """
        choices = self._get_choices()
        # If we don't have a list of choices we don't need to check
        if not choices:
            return False

        raise_value_error = False
        if self.attr_type in {list, tuple, set}:
            if set(value).difference(choices):
                raise_value_error = True

        elif value not in choices:
            raise_value_error = True

        return raise_value_error

    def validate(self, attr_name: str, value: Any, attr_type: type | UnionType | None = None) -> None:
        """
        Validates the value against the field's type and choices.

        Args:
            attr_name (str): The name of the attribute being validated.
            value (Any): The value to validate.
            attr_type (type | UnionType | None, optional): The expected type of the attribute. Defaults to None.

        Raises:
            FieldValueError: If the value is not valid according to the field's type and choices.
        """
        # Execute the normal validations
        super().validate(attr_name, value, attr_type)

        # Then we check if the value is in the choices
        if value not in (None, Undefined) and self._has_invalid_choices(value):
            msg = f"The value '{value}' for field '{attr_name}' must be in this list {self.choices}."
            raise FieldValueError(msg)


###############################################################################
#   BoolField Class Implementation
###############################################################################
class BoolField(Field):
    attr_type: bool = bool

    def __new__(cls, *args, **kwargs) -> bool:
        # This signature is used to change the default autocomplete for this class
        return super().__new__(cls, *args, **kwargs)

    def clean_value(self, value: Any) -> Any:
        """
        Converts the  given value to a boolean if possible using the 'convert_boolean' function.
        (Check the function's documentation for more information)

        Args:
            value (Boolean): The value to be converted. Can be of any type

        Returns:
            Any: The value converted to its boolean corresponding

        Example:
            >>> from everysk.core.fields import BoolField
            >>> bool_field = BoolField()
            >>> bool_field.clean_value("y")
            >>> True

            >>> bool_field.clean_value("n")
            >>> False

            >>> bool_field.clean_value("a")
            >>> ValueError: Invalid truth value 'a'
        """
        # https://docs.python.org/3/distutils/apiref.html#distutils.util.strtobool
        # The module distutils is deprecated, then we put the function code here
        if value is not None and value is not Undefined:
            value = bool_convert(value)

        return super().clean_value(value)


###############################################################################
#   DateField Class Implementation
###############################################################################
class DateField(Field):
    attr_type: Date = Date
    min_date: Date | Callable = None
    max_date: Date | Callable = None

    def __new__(cls, *args, **kwargs) -> Date:
        # This signature is used to change the default autocomplete for this class
        return super().__new__(cls, *args, **kwargs)

    def __init__(
        self,
        default: Any = None,
        *,
        min_date: Date = None,
        max_date: Date = None,
        required: bool = False,
        readonly: bool = False,
        required_lazy: bool = False,
        empty_is_none: bool = False,
        choices: set | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            default=default,
            min_date=min_date,
            max_date=max_date,
            required=required,
            readonly=readonly,
            required_lazy=required_lazy,
            empty_is_none=empty_is_none,
            choices=choices,
            **kwargs,
        )

    def clean_value(self, value: Any) -> Any:
        """
        Method simple converts Date strings to Date object in the Everysk format

        Args:
            value (Any): Desired date string to be converted

        Returns:
            A new Date object representing the converted date

        Raises:
            ValueError: If the string is not represented in either
                        ISO format ("YYYY-MM-DD") or Everysk format ("YYYYMMDD").

        Example:
            >>> from everysk.core.fields import DateField
            >>> date_field = DateField()
            >>> date_field.clean_value("20140314")
            Date(2014, 3, 14)
            >>> date_field.clean_value("2014-03-14")
            Date(2014, 3, 14)
        """
        if isinstance(value, str):
            if '-' in value:
                value = Date.fromisoformat(value)
            else:
                # Everysk format
                value = Date.strptime(value, '%Y%m%d')

        return super().clean_value(value)

    def validate(self, attr_name: str, value: Any, attr_type: type | UnionType | None = None) -> None:
        """
        Checks if value is greater than min and lower than max including both values.

        Args:
            attr_name (str): Name of the attribute used for error checking
            value (Any): Value used for validation
            attr_type (type | UnionType, optional): Type of the field we are trying to validate. Defaults to None.

        Returns:
            Either the value is between min_date and max_date

        Raises:
            FieldValueError: If the value is not between min_date and max_date

        Example:
            >>> from everysk.core.fields import DateField
            >>> from everysk.core.datetime import Date
            >>> date_field = DateField(min_date=Date(2023, 1, 1), max_date=Date(2023, 12, 31))

            >>> try:
            >>> ... date_field.validate("example_date", Date(2023, 6, 15))
            >>> ... print("June 15, 2023, is a valid date")
            >>> except Exception as e:
            >>> ... print(f"Validation error: {e}")
            >>> June 15, 2023, is a valid date

            >>> try:
            >>> ... date_field.validate("example_date", Date(2022, 12, 31))
            >>> ... print("December 31, 2022, is a valid date")
            >>> except Exception as e:
            >>> ... print(f"validation error: {e}")
            >>> Validation error: The value '2022-12-31' for field 'example_date' must be between 2023-01-01 and 2023-12-31.
        """  # noqa: E501
        _min_max_validate(self.min_date, self.max_date, value, attr_name)
        return super().validate(attr_name, value, attr_type)


###############################################################################
#   DateTimeField Class Implementation
###############################################################################
class DateTimeField(Field):
    attr_type: DateTime = DateTime
    min_date: DateTime | Callable = None
    max_date: DateTime | Callable = None
    force_time: str = None

    def __new__(cls, *args, **kwargs) -> DateTime:
        # This signature is used to change the default autocomplete for this class
        return super().__new__(cls, *args, **kwargs)

    def __init__(
        self,
        default: Any = None,
        *,
        min_date: DateTime = None,
        max_date: DateTime = None,
        force_time: str = 'FIRST_MINUTE',
        required: bool = False,
        readonly: bool = False,
        required_lazy: bool = False,
        empty_is_none: bool = False,
        choices: set | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            default=default,
            min_date=min_date,
            max_date=max_date,
            force_time=force_time,
            required=required,
            readonly=readonly,
            required_lazy=required_lazy,
            empty_is_none=empty_is_none,
            choices=choices,
            **kwargs,
        )

    def clean_value(self, value: Any) -> Any:
        """
        Converts a DateTime string to a DateTime object using the 'fromisoformat' function.
        (check 'fromisoformat' function for more information)

        Args:
            value (Any): desired DateTime string to be converted

        Returns:
            Any: a new DateTime object formatted

        Raises:
            ValueError: if the input is not formatted in the ISO format

        Example:
            >>> from everysk.core.fields import DateTimeField
            >>> date_time_field = DateTimeField()

            >>> date_time_field.clean_value("2023-03-15")
            >>> DateTime(2023, 3, 15, 0, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))

            >>> date_time_field.clean_value("2023-03-15T14:30:00")
            >>> DateTime(2023, 3, 15, 14, 30, tzinfo=zoneinfo.ZoneInfo(key='UTC'))

            >>> date_time_field.clean_value("14-03-2023")
            >>> ValueError: time data "14-03-2023" does not match format: "%Y-%m-%d"
        """
        # Convert DateTime strings to DateTime object
        if isinstance(value, str):
            if ':' not in value:
                value: DateTime = DateTime.fromisoformat(value).force_time(self.force_time)
            else:
                value: DateTime = DateTime.fromisoformat(value)
        elif Date.is_date(value):
            value: DateTime = DateTime.fromisoformat(value.isoformat())

        return super().clean_value(value)

    def validate(self, attr_name: str, value: Any, attr_type: type | UnionType | None = None) -> None:
        """
        Checks is the value passed is in the correct range between min and max,
        as well as required, required_lazy, and attribute_type validations.

        Args:
            attr_name (str): The name of the attribute being validated, used for identification in error messages.
            value (Any): The value to be validated for the specified attribute.
            attr_type (type | UnionType, optional):
                The expected type of the attribute. If provided, the value is checked to ensure it is of this type.
                Defaults to None.

        Raises:
            FieldValueError: if the value provided is not between min and max values

        Example:
            >>> from everysk.core.datetime import Date
            >>> from everysk.core.fields import DateTimeField
            >>> from everysk.core.datetime import DateTime
            >>> date_time_field = DateTimeField(min_date=DateTime(2023, 1, 1), max_date=DateTime(2023, 12, 31))

            >>> try:
            >>> ... date_time_field.validate("test_field", DateTime(2023, 6, 15))
            >>> ... print("Validation successful")
            >>> except FieldValueError as e:
            >>> ... print(f"Validation error: {e}")
        """
        _min_max_validate(self.min_date, self.max_date, value, attr_name)
        return super().validate(attr_name, value, attr_type)


###############################################################################
#   DictField Class Implementation
###############################################################################
class DictField(Field):
    # Field that supports a dictionary and BaseDict as a value.
    attr_type: dict | BaseDict = dict | BaseDict

    class ReadonlyDict(dict):
        __setitem__ = _do_nothing
        __delitem__ = _do_nothing
        pop = _do_nothing
        popitem = _do_nothing
        clear = _do_nothing
        update = _do_nothing
        setdefault = _do_nothing

    def __new__(cls, *args, **kwargs) -> dict | BaseDict:
        # This signature is used to change the default autocomplete for this class
        return super().__new__(cls, *args, **kwargs)

    def __init__(
        self,
        default: Any = None,
        *,
        required: bool = False,
        readonly: bool = False,
        required_lazy: bool = False,
        empty_is_none: bool = False,
        **kwargs,
    ) -> None:
        # When the field is readonly, we need to change the content to.
        if readonly and default:
            default = self.ReadonlyDict(default)

        super().__init__(
            default=default,
            required=required,
            readonly=readonly,
            required_lazy=required_lazy,
            empty_is_none=empty_is_none,
            **kwargs,
        )


###############################################################################
#   EmailField Class Implementation
###############################################################################
class EmailField(Field):
    attr_type: str = str

    def __new__(cls, *args, **kwargs) -> str:
        # This signature is used to change the default autocomplete for this class
        return super().__new__(cls, *args, **kwargs)

    def validate(self, attr_name: str, value: Any, attr_type: type | UnionType | None = None) -> None:
        """
        Validates if the value is an e-mail address.
        To validate we check the existence of the '@' character and the length of the string.

        Args:
            attr_name (str): The name of the attribute being validated, used for identification in error messages.
            value (Any): The value to be validated for the specified attribute.
            attr_type (type | UnionType, optional):
                The expected type of the attribute. If provided, the value is checked to ensure it is of this type.
                Defaults to None.

        Raises:
            FieldValueError: If the value is not an e-mail address.
        """
        # The maximum length of an email is 320 characters per RFC 3696 section 3,
        # and at least 3 digits a@b
        msg = f'Key {attr_name} must be an e-mail.'
        if (
            value is not None
            and value is not Undefined
            and isinstance(value, str)
            and ('@' not in value or len(value) > 320 or len(value) < 3)  # noqa: PLR2004
        ):
            raise FieldValueError(msg)

        try:
            # Get the cases where we could have more than one @ in the string
            user, domain = value.split('@')
        except ValueError as error:
            raise FieldValueError(msg) from error

        return super().validate(attr_name, value, attr_type)


###############################################################################
#   FloatField Class Implementation
###############################################################################
class FloatField(Field):
    attr_type: float = float
    min_size: float = None
    max_size: float = None

    def __new__(cls, *args, **kwargs) -> float:
        # This signature is used to change the default autocomplete for this class
        return super().__new__(cls, *args, **kwargs)

    def __init__(
        self,
        default: Any = None,
        *,
        min_size: float = float('-inf'),
        max_size: float = float('inf'),
        required: bool = False,
        readonly: bool = False,
        required_lazy: bool = False,
        empty_is_none: bool = False,
        choices: set | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            default=default,
            required=required,
            readonly=readonly,
            min_size=min_size,
            max_size=max_size,
            required_lazy=required_lazy,
            empty_is_none=empty_is_none,
            choices=choices,
            **kwargs,
        )

    def clean_value(self, value: Any) -> Any:
        """
        Convert a float string to a float object

        Args:
            value (Any): Value desired for conversion to float

        Returns:
            Float: if value is able to be converted to float object

        Raises:
            ValueError: If value could not be converted to a float

        Example:
            >>> from everysk.core.fields import FloatField
            >>> float_field = FloatField()

            >>> float_field.clean_value("3.14")
            >>> 3.14

            >>> float_field.clean_value(123)
            >>> 123.0

            >>> float_field.clean_value('abc')
            >>> ValueError: could not convert string to float: 'abc'
        """
        # Convert Float strings to float object
        if isinstance(value, (int, str)):
            value = float(value)

        return super().clean_value(value)

    def validate(self, attr_name: str, value: Any, attr_type: type | UnionType | None = None) -> None:
        """
        Checks if value is greater than min and lower than max including both values.

        Args:
            attr_name (str): The name of the attribute being validated, used for identification in error messages.
            value (Any): The value to be validated for the specified attribute.
            attr_type (type | UnionType, optional):
                The expected type of the attribute. If provided, the value is checked to ensure it is of this type.
                Defaults to None.

        Raises:
            FieldValueError: If value is not between min and max.

        Example:
            >>> from everysk.core.fields import FloatField
            >>> from everysk.core.exceptions import FieldValueError
            >>> float_field = FloatField(min_size=0.0, max_size=100.0)

            >>> try:
            >>> ... float_field.validate("test_field", 50.0)
            >>> ... print("Validation successful: 50.0 is within the range.")
            >>>  except FieldValueError as e:
            >>> ... print(f"Validation error: {e}")
            >>> Validation successful: 50.0 is within the range.

            >>> try:
            >>> ... float_field.validate("test_field", -10.0)
            >>> ... print("Validation successful: -10.0 is within the range.")
            >>>  except FieldValueError as e:
            >>> ... print(f"Validation error: {e}")
            >>> Validation error: The value '-10.0' for field 'test_field' is not within the allowed range.
        """
        _min_max_validate(min_value=self.min_size, max_value=self.max_size, value=value, attr_name=attr_name)
        return super().validate(attr_name, value, attr_type)


###############################################################################
#   IntField Class Implementation
###############################################################################
class IntField(Field):
    attr_type: int = int
    min_size: int = None
    max_size: int = None

    def __new__(cls, *args, **kwargs) -> int:
        # This signature is used to change the default autocomplete for this class
        return super().__new__(cls, *args, **kwargs)

    def __init__(
        self,
        default: Any = None,
        *,
        min_size: int = -max_int,
        max_size: int = max_int,
        required: bool = False,
        readonly: bool = False,
        required_lazy: bool = False,
        empty_is_none: bool = False,
        choices: set | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            default=default,
            required=required,
            readonly=readonly,
            min_size=min_size,
            max_size=max_size,
            required_lazy=required_lazy,
            empty_is_none=empty_is_none,
            choices=choices,
            **kwargs,
        )

    def clean_value(self, value: Any) -> Any:
        """
        Converts a value to an integer if it can be converted

        Args:
            value (Any): Value to convert

        Returns:
            Int: value converted to an integer

        Raises:
            ValueError: if the string cannot be converted to an integer

        Example:
            >>> from everysk.core.fields import IntField
            >>> int_field = IntField()

            >>> int_field.clean_value("123")
            >>> 123

            >>> int_field.clean_value("abc")
            >>> ValueError: invalid literal for int() with base 10: 'abc'
        """
        # Convert Int strings to int object
        if isinstance(value, str):
            value = int(value)

        return super().clean_value(value)

    def validate(self, attr_name: str, value: Any, attr_type: type | UnionType | None = None) -> None:
        """
        Checks if value is greater than min and lower than max including both values.

        Args:
            attr_name (str): The name of the attribute being validated, used for identification in error messages.
            value (Any): The value to be validated for the specified attribute.
            attr_type (type | UnionType, optional):
                The expected type of the attribute. If provided, the value is checked to ensure it is of this type.
                Defaults to None.

        Raises:
            FieldValueError: If value is not between min_size and max.

        Example:
            >>> from everysk.core.fields import IntField
            >>> from everysk.core.exceptions import FieldValueError
            >>> int_field = IntField(min_size=1, max_size=10)

            >>> try:
            >>> ... int_field.validate("test_field", 5)
            >>> ... print("Validation successful")
            >>> except FieldValueError as e:
            >>> ... print(f"Validation error: {e}")
            >>> Validation successful

            >>> try:
            >>> ... int_field.validate("test_field", -1)
            >>> ... print("validation successful")
            >>> except FieldValueError as e:
            >>> ...print(f"Validation error: {e}")
            >>> Validation error: The value '-1' for field 'test_field' must be between 1 and 10.
        """
        _min_max_validate(min_value=self.min_size, max_value=self.max_size, value=value, attr_name=attr_name)
        return super().validate(attr_name, value, attr_type)


###############################################################################
#   IteratorField Class Implementation
###############################################################################
class IteratorField(Field):
    attr_type: Iterator = Iterator

    def __new__(cls, *args, **kwargs) -> Iterator:
        # This signature is used to change the default autocomplete for this class
        return super().__new__(cls, *args, **kwargs)

    def clean_value(self, value: Any) -> Any:
        """
        Cleans the given value before storing it.

        Args:
            value (Any): The value to be cleaned.

        Returns:
            Any: The cleaned value.

        """
        # Convert List/Str to iterators
        if isinstance(value, (list, str)):
            value = iter(value)

        return super().clean_value(value)


###############################################################################
#   ListField
###############################################################################
class ListField(Field):
    """
    https://stackoverflow.com/questions/855191/how-big-can-a-python-list-get#comment112727918_15739630
    so on 64 systems is maxsize / 8
    """

    attr_type: list = list
    min_size: int = None
    max_size: int = None
    separator: str = ','

    class ReadonlyList(list):
        __setitem__ = _do_nothing
        __delitem__ = _do_nothing
        append = _do_nothing
        clear = _do_nothing
        extend = _do_nothing
        insert = _do_nothing
        pop = _do_nothing
        remove = _do_nothing
        reverse = _do_nothing
        sort = _do_nothing

    def __new__(cls, *args, **kwargs) -> list:
        # This signature is used to change the default autocomplete for this class
        return super().__new__(cls, *args, **kwargs)

    def __init__(
        self,
        default: Any = None,
        *,
        min_size: int = 0,
        max_size: int = max_int / 8,
        readonly: bool = False,
        required: bool = False,
        required_lazy: bool = False,
        separator: str = ',',
        empty_is_none: bool = False,
        **kwargs,
    ) -> None:
        if min_size < 0:
            raise FieldValueError('List min_size cloud not be a negative number.')

        # When the field is readonly, we need to change the content to.
        if readonly and (default is not None or default is not Undefined):
            default = self.ReadonlyList(default)

        super().__init__(
            default=default,
            min_size=min_size,
            max_size=max_size,
            readonly=readonly,
            required=required,
            required_lazy=required_lazy,
            separator=separator,
            empty_is_none=empty_is_none,
            **kwargs,
        )

    def clean_value(self, value: Any) -> Any:
        """
        Clean the value before storing it.
        This method is used to ensure that the value is in the correct format before storing it.
        This method checks if the value is a string and converts it into a list if necessary.
        It then calls the parent class's clean_value method to perform additional cleaning.

        Args:
            value (Any): The value to be cleaned.

        Returns:
            Any: The cleaned value.

        Example:
            >>> field = Field()
            >>> field.clean_value("example")
            ['example']
        """
        if isinstance(value, str):
            # When we receive environment vars or HTTP query params they are always strings with ',' as separator
            value = [item.strip() for item in value.split(self.separator)]

        return super().clean_value(value)

    def validate(self, attr_name: str, value: Any, attr_type: type | UnionType | None = None) -> None:
        """
        Checks if value is greater than min_size and lower than max_size including both values.

        Args:
            attr_name (str): The name of the attribute being validated, used for identification in error messages.
            value (Any): The value to be validated for the specified attribute.
            attr_type (type | UnionType, optional):
                The expected type of the attribute. If provided, the value is checked to ensure it is of this type.
                Defaults to None.

        Raises:
            FieldValueError: If value is not list instance or if is not between min_size and max_size
        """
        if value is not None and value is not Undefined:
            if not isinstance(value, list):
                msg = f"The '{attr_name}' value must be a list."
                raise FieldValueError(msg)
            if not self.min_size <= len(value) <= self.max_size:
                msg = f"The attribute '{attr_name}' is not within the specified list range. min_size: {self.min_size} max_size: {self.max_size}"  # noqa: E501
                raise FieldValueError(msg)

        super().validate(attr_name, value, attr_type)


###############################################################################
#   SetField Class Implementation
###############################################################################
class SetField(Field):
    attr_type: set = set
    min_size: int = None
    max_size: int = None

    class ReadonlySet(set):
        __setitem__ = _do_nothing
        __delitem__ = _do_nothing
        add = _do_nothing
        clear = _do_nothing
        discard = _do_nothing
        pop = _do_nothing
        remove = _do_nothing
        update = _do_nothing

    def __new__(cls, *args, **kwargs) -> set:
        # This signature is used to change the default autocomplete for this class
        return super().__new__(cls, *args, **kwargs)

    def __init__(
        self,
        default: Any = None,
        *,
        min_size: int = 0,
        max_size: int = max_int / 8,
        readonly: bool = False,
        required: bool = False,
        required_lazy: bool = False,
        empty_is_none: bool = False,
        choices: set | None = None,
        **kwargs,
    ) -> None:
        if min_size < 0:
            raise FieldValueError('Set min_size cloud not be a negative number.')

        # When the field is readonly, we need to change the content to.
        if readonly and (default is not None or default is not Undefined):
            default = self.ReadonlySet(default)

        super().__init__(
            default=default,
            min_size=min_size,
            max_size=max_size,
            readonly=readonly,
            required=required,
            required_lazy=required_lazy,
            empty_is_none=empty_is_none,
            choices=choices,
            **kwargs,
        )

    def validate(self, attr_name: str, value: Any, attr_type: type | UnionType | None = None) -> None:
        """
        Checks if value is greater than min_size and lower than max_size including both values.

        Args:
            attr_name (str): The name of the attribute being validated, used for identification in error messages.
            value (Any): The value to be validated for the specified attribute.
            attr_type (type | UnionType, optional):
                The expected type of the attribute. If provided, the value is checked to ensure it is of this type.
                Defaults to None.

        Raises:
            FieldValueError: If value is not set instance.
            FieldValueError: If value is not between min_size and max_size.
        """
        super().validate(attr_name, value, attr_type)

        if value is not None and value is not Undefined and not self.min_size <= len(value) <= self.max_size:
            msg = f"The attribute '{attr_name}' is not within the specified set range. min_size: {self.min_size} max_size: {self.max_size}"  # noqa: E501
            raise FieldValueError(msg)


###############################################################################
#   StrField Class Implementation
###############################################################################
class StrField(Field):
    """
    Represents a string field in an entity.
    This field type is used to store string values and provides validation
    for string attributes based on specified constraints such as minimum and maximum size
    and regular expression pattern matching.

    Args:
        default (Any, optional): The default value for the field. Defaults to None.
        min_size (int, optional): The minimum allowed length for the string. Defaults to 0.
        max_size (int, optional): The maximum allowed length for the string. Defaults to the maximum integer value.
        regex (str, optional): The regular expression pattern to match against the string value. Defaults to None.
        readonly (bool, optional): Whether the field is read-only. Defaults to False.
        required (bool, optional): Whether the field is required. Defaults to False.
        required_lazy (bool, optional): Whether the field is lazily required. Defaults to False.
        empty_is_none (bool, optional): Whether an empty string should be treated as None. Defaults to False.

    Raises:
        FieldValueError: If the minimum size is negative
    """

    attr_type: str = str
    min_size: int = None
    max_size: int = None
    regex: re.Pattern = None

    def __new__(cls, *args, **kwargs) -> str:
        # This signature is used to change the default autocomplete for this class
        return super().__new__(cls, *args, **kwargs)

    def __init__(
        self,
        default: Any = None,
        *,
        min_size: int = 0,
        max_size: int = max_int,
        regex: str | None = None,
        readonly: bool = False,
        required: bool = False,
        required_lazy: bool = False,
        empty_is_none: bool = False,
        choices: set | None = None,
        **kwargs,
    ) -> None:
        if min_size < 0:
            msg = 'String min_size cloud not be a negative number.'
            raise FieldValueError(msg)

        super().__init__(
            default=default,
            regex=regex,
            min_size=min_size,
            max_size=max_size,
            readonly=readonly,
            required=required,
            required_lazy=required_lazy,
            empty_is_none=empty_is_none,
            choices=choices,
            **kwargs,
        )

    def validate(self, attr_name: str, value: Any, attr_type: type | UnionType | None = None) -> None:
        """
        Validates a string for its size and regex if they are specified.

        Args:
            attr_name (str): The name of the attribute being validated, used for identification in error messages.
            value (Any): The value to be validated for the specified attribute.
            attr_type (type | UnionType, optional):
                The expected type of the attribute. If provided, the value is checked to ensure it is of this type.
                Defaults to None.

        Raises:
            FieldValueError: If the value does not match a regex, is not the
            correct type, or is an invalid length.
        """
        # First let all default checks be done.
        super().validate(attr_name, value, attr_type)

        if self.regex and value and value is not Undefined and not self.regex.match(value):
            msg = f"The value '{value}' for field '{attr_name}' must match with this regex: {self.regex.pattern}."
            raise FieldValueError(msg)

        # Then we check for the size.
        try:
            if value is not None and value is not Undefined:
                _min_max_validate(
                    min_value=self.min_size, max_value=self.max_size, value=len(value), attr_name=attr_name
                )
        except FieldValueError as error:
            msg = f"The length '{len(value)}' for attribute '{attr_name}' must be between '{self.min_size}' and '{self.max_size}'."  # noqa: E501
            raise FieldValueError(msg) from error


# This field is legacy, the choice is already implemented in all fields.
# So we just inherit from StrField to keep compatibility.
class ChoiceField(StrField):
    pass


###############################################################################
#   RegexField Class Implementation
###############################################################################
class RegexField(Field):
    attr_type: re.Pattern = re.Pattern

    def __new__(cls, *args, **kwargs) -> re.Pattern:
        # This signature is used to change the default autocomplete for this class
        return super().__new__(cls, *args, **kwargs)

    def __init__(
        self,
        default: Any = None,
        *,
        readonly: bool = False,
        required: bool = False,
        required_lazy: bool = False,
        empty_is_none: bool = False,
        choices: set | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            default=default,
            readonly=readonly,
            required=required,
            required_lazy=required_lazy,
            empty_is_none=empty_is_none,
            choices=choices,
            **kwargs,
        )

    def clean_value(self, value: Any) -> Any:
        """
        Clean the value by compiling it into a regular expression pattern.

        This method takes a value and compiles it into a regular expression pattern if it is a string.
        If the value is equal to the default value, it updates the default value with the compiled pattern.
        It then calls the parent class's clean_value method to perform any additional cleaning.

        Args:
            value (Any): The value to be cleaned.

        Returns:
            Any: The cleaned value.

        Example:
            >>> field = RegexField(default='[0-9]+')
            >>> field.clean_value('123')
            re.compile('[0-9]+')
        """
        if isinstance(value, str):
            value = re.compile(value)

        return super().clean_value(value)


###############################################################################
#   TupleField Class Implementation
###############################################################################
class TupleField(Field):
    attr_type: tuple = tuple

    def __new__(cls, *args, **kwargs) -> tuple:
        # This signature is used to change the default autocomplete for this class
        return super().__new__(cls, *args, **kwargs)


###############################################################################
#   URLField Class Implementation
###############################################################################
class URLField(Field):
    attr_type: str = str
    supported_schemes: set = ('http', 'https', 'ftp', 'ftps', 'git')

    def __new__(cls, *args, **kwargs) -> str:
        # This signature is used to change the default autocomplete for this class
        return super().__new__(cls, *args, **kwargs)

    def validate(self, attr_name: str, value: Any, attr_type: type | UnionType | None = None) -> None:
        """
        Validates a URL string to ensure it is a valid URL.
        We check the protocol HTTP, HTTPS, FTP, FTPS, the domain format and size and the port number.

        Args:
            attr_name (str): The name of the attribute being validated, used for identification in error messages.
            value (Any): The value to be validated for the specified attribute.
            attr_type (type | UnionType, optional):
                The expected type of the attribute. If provided, the value is checked to ensure it is of this type.
                Defaults to None.

        Raises:
            FieldValueError: If the url is invalid.
        """
        if isinstance(value, str):
            # https://github.com/django/django/blob/main/django/core/validators.py
            ul = '\u00a1-\uffff'  # Unicode letters range (must not be a raw string).

            # IP patterns
            ipv4_re = (
                r'(?:0|25[0-5]|2[0-4][0-9]|1[0-9]?[0-9]?|[1-9][0-9]?)'
                r'(?:\.(?:0|25[0-5]|2[0-4][0-9]|1[0-9]?[0-9]?|[1-9][0-9]?)){3}'
            )
            ipv6_re = r'\[[0-9a-f:.]+\]'  # (simple regex, validated later)

            # Host patterns
            hostname_re = r'[a-z' + ul + r'0-9](?:[a-z' + ul + r'0-9-]{0,61}[a-z' + ul + r'0-9])?'

            # Max length for domain name labels is 63 characters per RFC 1034 sec. 3.1
            domain_re = r'(?:\.(?!-)[a-z' + ul + r'0-9-]{1,63}(?<!-))*'
            tld_re = (
                r'\.'  # dot
                r'(?!-)'  # can't start with a dash
                r'(?:[a-z' + ul + '-]{2,63}'  # domain label
                r'|xn--[a-z0-9]{1,59})'  # or punycode label
                r'(?<!-)'  # can't end with a dash
                r'\.?'  # may have a trailing dot
            )
            host_re = '(' + hostname_re + domain_re + tld_re + '|localhost)'

            regex = re.compile(
                r'^(?:[a-z0-9.+-]*)://'  # scheme is validated separately
                r'(?:[^\s:@/]+(?::[^\s:@/]*)?@)?'  # user:pass authentication
                r'(?:' + ipv4_re + '|' + ipv6_re + '|' + host_re + ')'
                r'(?::[0-9]{1,5})?'  # port
                r'(?:[/?#][^\s]*)?'  # resource path
                r'\Z',
                re.IGNORECASE,
            )
            msg = f'Key {attr_name} must be an URL.'
            if not regex.match(value):
                raise FieldValueError(msg)

            # The scheme needs a separate check
            try:
                result = urlparse(value)
                if result.scheme not in self.supported_schemes:
                    raise FieldValueError(msg)

            except ValueError:
                raise FieldValueError(msg) from ValueError

        return super().validate(attr_name, value, attr_type)
