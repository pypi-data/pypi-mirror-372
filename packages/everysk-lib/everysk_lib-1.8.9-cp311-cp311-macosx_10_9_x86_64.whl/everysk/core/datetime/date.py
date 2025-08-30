###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from datetime import date, datetime # pylint: disable=import-self
from typing import Any, Union, Self

from everysk.core.datetime import date_settings
from everysk.core.datetime.date_expression import DateExpressionMixin
from everysk.core.datetime.date_mixin import DateMixin


class Date(DateMixin, DateExpressionMixin, date): #pylint: disable=inherit-non-class

    @classmethod
    def ensure(cls, value: Any) -> Self:
        """
        Ensure that a value is a Date object or convert it to one.

        This class method takes a value and ensures that it is a Date object. If the value is a datetime.date object, it will be
        converted to a Date object by extracting the year, month, and day components. If the value is already a Date object, it
        will be returned as is. If the value is neither a Date object nor a datetime.date object, a ValueError is raised.

        Args:
            value (Any): The value to ensure as a Date object.

        Raises:
            ValueError: If the value cannot be converted to a Date object.

        Returns:
            Date: A Date object representing the same date as the input value.

        Example:
            Ensure a value is a Date object:
            >>> date_value = Date(2023, 7, 31)
            >>> Date.ensure(date_value)
            Date(2023, 7, 31)

            >>> datetime_date = datetime.date(2023, 7, 31)
            >>> Date.ensure(datetime_date)
            Date(2023, 7, 31)

        """
        if value.__class__ != cls:
            try:
                value = cls(value.year, value.month, value.day)
            except Exception:
                raise ValueError(f"Invalid instantiation of class '{cls.__name__}' from '{value.__class__.__name__}'") # pylint: disable=raise-missing-from

        return value

    @classmethod
    def fromisoformat(cls, date_string: str) -> Self:
        """
        Convert an ISO formatted date string to a Date object.

        This class method takes an ISO formatted date string and converts it to a Date object.

        Args:
            date_string (str): The ISO formatted date string to convert to a Date object.

        Raises:
            ValueError: If the input date string does not have the expected format.

        Returns:
            Date: A Date object representing the date extracted from the input ISO formatted date string.

        Example:
            Convert an ISO formatted date string to a Date object:
            >>> input_string = '20230101'
            >>> Date.fromisoformat(input_string)
            Date(2023, 1, 1)

            >>> input_string = '2023-01-01'
            >>> Date.fromisoformat(input_string)
            Date(2023, 1, 1)

        """
        if date_string and len(date_string) == 8:
            return cls.strptime(date_string)

        return super().fromisoformat(date_string)

    # antes retornava string, agora retorna self date
    # agora start_date é date
    @classmethod
    def fromordinal(cls, date_ordinal: int, start_date: 'Date' = None) -> Self:
        """
        Convert the ordinal day count since a base date to a Date object.

        This static method takes an `date_ordinal`, which is the number of days since a specified `start_date`,
        and converts it into a Date object.

        Args:
            date_ordinal (int): The ordinal day count since the base date specified by `start_date`.
            start_date (Date, optional): The base date to start counting from. Defaults to January 1, 1 AD (00010101).

        Raises:
            TypeError: If the input date_ordinal is not an integer.
            AttributeError: If the start date is not a Date object or None.

        Returns:
            Date: A Date object representing the date calculated from the ordinal day count and start_date.

        Example:
            Convert an ordinal day count to a Date object:
            >>> Date.fromordinal(1)
            Date(1, 1, 1)

            >>> Date.fromordinal(365)
            Date(1, 12, 31)

        """
        if start_date:
            date_ordinal += start_date.toordinal() - 1

        return super().fromordinal(date_ordinal)

    @classmethod
    def strptime(cls, date_string: str, format: str = date_settings.DEFAULT_DATE_FORMAT) -> Self: # pylint: disable=redefined-builtin
        """
        Convert a string to a Date object using the specified format.

        This static method takes a string and attempts to convert it into a Date object using the provided
        format. If the conversion is successful, the resulting Date object is returned. If the input string is
        empty or cannot be converted, a ValueError is raised.

        Args:
            date_string (str): The input string to be converted to a Date object.
            format (str, optional): The format string used to interpret the input string. Defaults to DEFAULT_DATE_FORMAT ('%Y%m%d').

        Raises:
            ValueError: If the input string is empty or cannot be converted to a Date object using the specified format.

        Returns:
            Date: A Date object representing the converted date if successful.

        Example:
            >>> date_str = '20230731'
            >>> Date.string_to_date(date_str)
            Date(2023, 7, 31)

        """
        datetime_ = datetime.strptime(date_string, format) # pylint: disable=no-member
        return cls(datetime_.year, datetime_.month, datetime_.day)

    @classmethod
    def strptime_or_null(cls, date_string: str, format: str = date_settings.DEFAULT_DATE_FORMAT) -> Union[Self, None]: # pylint: disable=redefined-builtin
        """
        Convert a string to a Date object using the specified format or return None.

        This class method takes a string and attempts to convert it into a Date object using the provided
        format. If the conversion is successful, the resulting Date object is returned. If the input string is
        empty or cannot be converted, the method returns None.

        Args:
            date_string (str): The input string to be converted to a Date object.
            format (str, optional): The format string used to interpret the input string. Defaults to DEFAULT_DATE_FORMAT ('%Y%m%d').

        Returns:
            Date or None: A Date object representing the converted date if successful, or None if the input string is empty or cannot be converted.

        Example:
            To convert a string to a Date object:
            >>> date_string = '20230731'
            >>> date_obj = Date.strptime_or_null(date_string)
        """
        date_ = None

        try:
            date_ = Date.strptime(date_string, format=format)
        except Exception: # pylint: disable=broad-exception-caught
            pass

        return date_

    @classmethod
    def is_string_date(cls, date_string: str, format: str = date_settings.DEFAULT_DATE_FORMAT) -> bool: # pylint: disable=redefined-builtin
        """
        Check if a string is a valid representation of a date.

        This class method checks if the input string is a valid representation of a date
        using the specified date format. If the input string can be successfully converted to a
        Date object using the provided format, the method returns True. Otherwise, it returns False.

        Args:
            date_string (str): The string to check for validity as a date representation.
            format (str, optional): The format string used to interpret the input string. Defaults to DEFAULT_DATE_FORMAT ('%Y%m%d').

        Returns:
            bool: True if the input string is a valid date representation, False otherwise.

        Example:
            To check if a string is a valid date representation:
            >>> date_string = '20230731'
            Date.is_string_date(date_string)
            True

            >>> date_string = '2023-05-01'
            Date.is_string_date(date_string)
            False

            >>> date_string = '2023-05-01'
            Date.is_string_date(date_string, format='%Y-%m-%d')
            True
        """
        return bool(cls.strptime_or_null(date_string, format=format))

    def strftime(self, format: str = date_settings.DEFAULT_DATE_FORMAT) -> str: # pylint: disable=redefined-builtin, useless-parent-delegation
        """
        Convert a `Date` object to a date string representation.

        This instance method takes a `Date` object and converts it to a date string representation
        using the specified date `format`. If no `format` is provided, the method will use the Everysk's default date
        format `DEFAULT_DATE_FORMAT`.

        Args:
            format (str, optional): The desired date format. This should be a string representing the desired format using the appropriate format codes. (default is `DEFAULT_DATE_FORMAT`)

        Raises:
            TypeError: If a invalid argument is provided.

        Returns:
            str: The date string representation of the input `Date` object in the specified date format.

        Example:
            To convert a `Date` object to a date string:
            >>> date_obj = Date(2023, 7, 31)
            >>> date_obj.strftime(format='%d/%m/%Y')
            '31/07/2023'

        """
        return super().strftime(format)

    @classmethod
    def strftime_or_null(cls, date_: Any, format: str = date_settings.DEFAULT_DATE_FORMAT) -> Union[str, None]: # pylint: disable=redefined-builtin
        """
        Convert a Date object to a string representation or return None.

        This class method takes a Date object and converts it to a string representation
        using the default date format ('%Y%m%d'), which represents dates in the format 'YYYYMMDD'.
        If the input date is None, the method returns None.

        Args:
            date_ (Date or None): The Date object to convert to a string representation, or None.
            format (str, optional): The desired date format. This should be a string representing the desired format using the appropriate format codes. (default is `DEFAULT_DATE_FORMAT`)

        Returns:
            str or None: A string representation of the input date in the specified date format, or None if the input date is None.

        Example:
            To convert a Date object to a date string or return None:
            >>> import datetime
            >>> date_obj = Date(2023, 7, 31)
            >>> Date.strftime_or_null(date_obj)
            '20230731'

            >>> Date.strftime_or_null(None)
            None
        """
        if date_ is not None:
            try:
                date_ = date_.strftime(format=format)
            except Exception: # pylint: disable=broad-exception-caught
                date_ = None

        return date_

    @classmethod
    def is_date(cls, value: Any) -> bool:
        """
        Check if a value is a Date object.

        This class method checks if the input value is an instance of the `Date` class.

        Args:
            value (Any): The value to be checked.

        Returns:
            bool: True if the input value is a Date object, False otherwise.

        Example:
            >>> date_obj = Date(2023, 7, 31)
            >>> Date.is_date(date_obj)
            True

            >>> date_time_obj = DateTime(2023, 7, 31, 12, 0)
            >>> Date.is_date(date_time_obj)
            False
        """
        if value is not None:
            if value.__class__ in (Date, date):
                return True

        return False

    def is_today(self) -> bool:
        """
        Check if the current date corresponds to the date represented by this Date object.

        This method compares the date represented by this Date object with the current date and returns True if they are the same.

        Returns:
            bool: True if this Date object represents the current date, False otherwise.

        Example:
            >>> today = Date.today()
            >>> today.is_today()
            True

            >>> future_date = Date(2023, 12, 31)
            >>> future_date.is_today()
            False
        """
        return self == Date.today()

    def date(self) -> Self:
        """
        Return Date object with same year, month and day. Used to maintain consistency between DateTime and Date instances

        Returns:
            Date: A Date object representing the same date as the input value.

        Example:
            >>> today = Date(2023, 12, 31)
            >>> today.date()
            Date(2023, 12, 31)
        """
        return self

    ####################################
    ### DATE RANGE
    ####################################

    @classmethod
    def date_range(cls, range_type: str, period: str, n_period: int, start_date: 'Date', end_date: 'Date') -> tuple[str, str]:
        """
        Get the start date and end date based on specified parameters.

        This method returns a tuple of two dates (start_date and end_date) based on the provided parameters. It is useful for generating date ranges based on different requirements.

        Args:
            range_type (str): Specifies the type of range needed. Possible values: 'single_date', 'custom_range', 'n_period', 'period_to_date', 'end_period_to_date'.
            period (str): Specifies the type of period in case `range_type` is 'n_period' or 'period_to_date'. Possible values: 'days', 'weeks', 'months', 'years', 'mtd', 'qtd', 'ytd'.
            n_period (int): Specifies the number of periods to be considered in case `range_type` is 'n_period'.
            start_date (Date): The start date of the custom range in case `range_type` is 'custom_range'.
            end_date (Date): The end date of the custom range in case `range_type` is 'custom_range' or 'single_date'.

        Returns:
            tuple[str, str]: A tuple of start date and end date in string format ('YYYYMMDD').

        Raises:
            ValueError: If an invalid `endDate`, `startDate`, `nPeriod`, `period`, or `range_type` is provided.

        Example:
            >>> Date.date_range('single_date', None, None, None, Date(2023, 1, 10))
            ('20230110', '20230110')

            >>> Date.date_range('custom_range', None, None, Date(2023, 1, 1), Date(2023, 1, 10))
            ('20230101', '20230110')

            >>> Date.date_range('n_period', 'months', 3, None, Date(2023, 1, 10))
            ('20231010', '20230110')

            >>> Date.date_range('period_to_date', 'ytd', None, None, Date(2023, 12, 31))
            ('20230101', '20231231')
        """
        if start_date and start_date.__class__ != Date:
            raise ValueError('Invalid start_date type')

        if end_date and end_date.__class__ != Date:
            raise ValueError('Invalid end_date type')

        if not end_date:
            end_date = Date.today()

        date_ = end_date

        if range_type == 'single_date':
            start_date = end_date

        elif range_type == 'custom_range':
            if not start_date:
                start_date = cls.ensure(date_settings.MARKET_START_DATE)

        elif range_type == 'n_period':
            delta = -int(n_period)

            if period == 'days':
                start_date = date_.delta(period=delta, periodicity='D')
            elif period == 'weeks':
                start_date = date_.delta(period=delta, periodicity='W')
            elif period == 'months':
                start_date = date_.delta(period=delta, periodicity='M')
            elif period == 'years':
                start_date = date_.delta(period=delta, periodicity='Y')
            else:
                raise ValueError('invalid n period')

        elif range_type in ('period_to_date', 'end_period_to_date'):
            if period == 'mtd':
                start_date = end_date
                start_date = start_date.replace(day=1)
            elif period == 'qtd':
                start_date = Date(date_.year, 3 * date_.quarter - 2, 1)
            elif period == 'ytd':
                start_date = end_date
                start_date = start_date.replace(month=1, day=1)
            else:
                raise ValueError('invalid period to date')

            if range_type == 'end_period_to_date':
                start_date = start_date.delta(period=-1, periodicity='B')
        else:
            raise ValueError('invalid range type')

        assert (start_date and end_date)

        return (start_date, end_date)
