###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from datetime import datetime, timezone #pylint: disable=import-self
from typing import Any, Union, Self
from zoneinfo import ZoneInfo

from everysk.core.datetime.date_mixin import DateMixin
from everysk.core.datetime import date_settings


class DateTime(DateMixin, datetime): #pylint: disable=inherit-non-class

    def __new__(cls, year: int, month: int = None, day: int = None, hour: int = 0, minute: int = 0, second: int = 0, microsecond: int = 0, tzinfo: ZoneInfo = None, fold: int = 0) -> Self:
        """
        Create a new DateTime object.

        Args:
            year (int): The year.
            month (int, optional): The month. Defaults to None.
            day (int, optional): The day. Defaults to None.
            hour (int, optional): The hour. Defaults to 0.
            minute (int, optional): The minute. Defaults to 0.
            second (int, optional): The second. Defaults to 0.
            microsecond (int, optional): The microsecond. Defaults to 0.
            tzinfo (ZoneInfo, optional): The time zone information. Defaults to None (UTC).
            fold (int, optional): Fold value (0 or 1). Defaults to 0.

        Raises:
            ValueError: If the input values are not valid for creating a DateTime object.

        Returns:
            DateTime: A new DateTime object.

        Example:
            Create a DateTime object:
            >>> DateTime(2023, 9, 15, tzinfo=ZoneInfo('US/Eastern'))
            DateTime(2023, 9, 15, 0, 0, tzinfo=zoneinfo.ZoneInfo(key='US/Eastern'))

        See Also:
            [Python Documentation](https://docs.python.org/3/library/datetime.html#datetime.datetime.fold)
        """
        # We check for tzinfo to enforce the UTC if empty
        if not tzinfo:
            tzinfo = ZoneInfo('UTC')

        args = (year, month, day, hour, minute, second, microsecond)
        kwargs = {'tzinfo': tzinfo, 'fold': fold}
        # To keep the pickle support we need to check the year param
        # and we must keep month and day optional on the class initialization.
        if isinstance(year, (bytes, str)):
            # When we not provide the tzinfo, month will be empty
            if not month:
                month = tzinfo
            args = (year, month)
            kwargs = {}

        return super().__new__(cls, *args, **kwargs)

    @classmethod
    def ensure(cls, value: 'DateTime') -> Self:
        """
        Ensure that the provided value is an instance of DateTime.

        Args:
            value (DateTime): The value to ensure as a DateTime object.

        Raises:
            ValueError: If the provided value cannot be converted to a DateTime object.

        Returns:
            DateTime: A DateTime object.

        Example:
            Ensure a value is a DateTime object:
            >>> DateTime.ensure(datetime(2023, 9, 15))
            DateTime(2023, 9, 15, 0, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))
            >>> DateTime.ensure(DateTime(2023, 9, 15))
            DateTime(2023, 9, 15, 0, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))
            >>> DateTime.ensure(DatetimeWithNanoseconds(2023, 9, 15))
            DateTime(2023, 9, 15, 0, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))
        """
        try:
            value = cls(value.year, value.month, value.day, value.hour, value.minute, value.second, value.microsecond, value.tzinfo)
        except AttributeError as error:
            raise ValueError(f"Invalid instantiation of class '{cls.__name__}' from '{value.__class__.__name__}'") from error

        return value

    @classmethod
    def fromtimestamp(cls, timestamp: float, tz: ZoneInfo = None) -> Self:
        """
        Create a DateTime object from a timestamp number.

        Args:
            timestamp (float): A number representing a DateTime object in float format.
            tz (ZoneInfo, optional): The time zone information. Defaults to None (UTC).

        Raises:
            ValueError: If the timestamp is not a valid number.

        Returns:
            DateTime: A DateTime object created from the timestamp.

        Example:
            Create a DateTime object from a timestamp:
            >>> DateTime.fromtimestamp(1631702400.0, ZoneInfo('US/Eastern'))
            DateTime(2021, 9, 15, 6, 40, tzinfo=zoneinfo.ZoneInfo(key='US/Eastern'))
        """
        if tz is None:
            tz = ZoneInfo('UTC')
        return super().fromtimestamp(timestamp, tz)

    # OLD date_time_adjust_time_zone
    def adjust_time_zone(self, time_zone: str = date_settings.DEFAULT_TIME_ZONE) -> Self:
        """
        Adjust the time zone of a DateTime object by replacing its timezone information.

        Args:
            time_zone (str, optional): The time zone string to set for the date and time object.
                Should be a valid time zone string recognized by `zoneinfo.ZoneInfo`.
                Defaults to the value of `date_settings.DEFAULT_TIME_ZONE`.

        Raises:
            ValueError: If the provided `time_zone` string is not a valid time zone.

        Returns:
            DateTime: A new DateTime object with the replaced timezone information.

        Example:
            To adjust the time zone of a DateTime object:
            >>> date_time_obj = DateTime(2023, 7, 31, 12, 34, 56)
            >>> date_time_obj.adjust_time_zone(time_zone='America/New_York')
            DateTime(2023, 7, 31, 12, 34, 56, tzinfo=zoneinfo.ZoneInfo(key='America/New_York'))
        """
        tz = ZoneInfo(time_zone)
        return self.replace(tzinfo=tz)

    def astimezone(self, tz: str = date_settings.DEFAULT_TIME_ZONE) -> Self:
        """
        Adjust the time zone of a DateTime object using the underlying superclass method.

        Args:
            tz (str, optional): The time zone string to use for adjusting the date and time.
                Should be a valid time zone string recognized by `zoneinfo.ZoneInfo`.
                Defaults to the value of `date_settings.DEFAULT_TIME_ZONE`.

        Returns:
            DateTime: A new DateTime object representing the adjusted date and time in the specified time zone.

        Example:
            >>> date_time_obj = DateTime(2023, 7, 31, 12, 34, 56)
            >>> date_time_obj.astimezone(tz='America/New_York')
            DateTime(2023, 7, 31, 8, 34, 56, tzinfo=zoneinfo.ZoneInfo(key='America/New_York'))
        """
        if isinstance(tz, str):
            tz = ZoneInfo(tz)
        return super().astimezone(tz)

    @classmethod
    def now(cls, tzinfo: timezone = None) -> Self:
        """
        Get the current DateTime object for a specified time zone.

        Args:
            tzinfo (timezone, str, optional): The time zone information.
                - If not provided, it defaults to 'UTC'.
                - If a string is provided, it's used to create a `zoneinfo.ZoneInfo` object.

        Raises:
            ValueError: If the provided `tzinfo` is not a valid time zone.

        Returns:
            DateTime: A DateTime object representing the current date and time in the specified time zone.

        Example:
            Get the current DateTime object in a specific time zone:
            >>> DateTime.now(tzinfo='America/New_York')
            DateTime(2023, 9, 15, 10, 30, 0, tzinfo=zoneinfo.ZoneInfo(key='America/New_York'))
        """
        if tzinfo is None:
            tzinfo = ZoneInfo('UTC')
        elif isinstance(tzinfo, str):
            tzinfo = ZoneInfo(tzinfo)
        return super().now(tzinfo)

    @classmethod
    def fromisoformat(cls, date_string: str) -> Self:
        """
        Convert ISO formatted date and datetime strings to a `DateTime` object.

        Args:
            date_string (str):
                The ISO formatted date or datetime string to convert to a `DateTime` object.

        Raises:
            ValueError: If the input date_string is not in a valid ISO format.

        Returns:
            DateTime: A `DateTime` object representing the date and time extracted from the input ISO formatted string.

        Examples:
            Convert ISO formatted date or datetime strings to `DateTime` objects:
            >>> DateTime.fromisoformat('20230101')
            DateTime(2023, 1, 1, 0, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))

            >>> DateTime.fromisoformat('2023-01-01')
            DateTime(2023, 1, 1, 0, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))

            >>> DateTime.fromisoformat('2023-01-01T00:00:00')
            DateTime(2023, 1, 1, 0, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))

            >>> DateTime.fromisoformat('20230101 00:00:00')
            DateTime(2023, 1, 1, 0, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))

            >>> DateTime.fromisoformat('2023-01-01T00:00:00+00:00')
            DateTime(2023, 1, 1, 0, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))

            >>> DateTime.fromisoformat('2023-01-01 00:00:00+00:00')
            DateTime(2023, 1, 1, 0, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))

            >>> DateTime.fromisoformat('2023-01-01T00:00:00.000000Z')
            DateTime(2023, 1, 1, 0, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))

            >>> DateTime.fromisoformat('2023-01-01 00:00:00.000000Z')
            DateTime(2023, 1, 1, 0, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))
        """
        if date_string:
            # This Z format is not native, we need to implement.
            if date_string[-1] == 'Z':
                # 2023-08-08T21:29:54.5713046Z -> This is from Refinitiv
                if '.' in date_string:
                    # We need to get all numbers after the '.'
                    milliseconds = date_string[date_string.index('.') + 1:-1]

                    # Then we need to transform to be 6 length exact
                    # rjust will put 0 to the right until reach 6 in size
                    correct_milliseconds = milliseconds.rjust(6, '0')[:6]

                    # Then we generate the correct new __date_string
                    date_string = date_string.replace(milliseconds, correct_milliseconds)

                # Z is used to represent UTC
                date_string = date_string.replace('Z', '+00:00')
            elif len(date_string) == 8:
                return cls.strptime(date_string, '%Y%m%d')
            elif len(date_string) == 10:
                return cls.strptime(date_string, '%Y-%m-%d')
            elif len(date_string) == 17 and ' ' in date_string:
                return cls.strptime(date_string)

        return super().fromisoformat(date_string).astimezone('UTC')

    # OLD date_time_to_timestamp
    def timestamp(self) -> int:
        """
        Get the timestamp of the DateTime object.

        Returns:
            int: The timestamp as an integer representing the number of seconds since the Unix epoch.

        Example:
            Get the timestamp of a DateTime object:
            >>> dt = DateTime(2023, 9, 15, 12, 0)
            >>> dt.timestamp()
            1694779200
        """
        return int(super().timestamp())

    def force_time(self, force_time: str = date_settings.DEFAULT_FORCE_TIME) -> Self:
        """
        Force a specific time on the DateTime object.

        This method allows you to force a specific time on the DateTime object based on the provided `force_time` parameter.

        Args:
            force_time (str, optional): The time to be forced on the DateTime object.
                - 'MIDDAY': Sets the time to 12:00:00.
                - 'NOW': Sets the time to the current time.
                - 'FIRST_MINUTE': Sets the time to 00:00:00.
                - 'LAST_MINUTE': Sets the time to 23:59:59.
                - Defaults to 'MIDDAY'.

        Raises:
            ValueError: If an invalid `force_time` is provided.

        Returns:
            DateTime: A new DateTime object with the forced time.

        Example:
            Force a specific time on a DateTime object:
            >>> dt = DateTime(2023, 9, 15, 0, 0)
            >>> dt.force_time('MIDDAY')
            DateTime(2023, 9, 15, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))
        """
        hour, minute, second, microsecond = None, None, None, None

        if force_time == 'MIDDAY':
            hour, minute, second, microsecond = 12, 0, 0, 0
        elif force_time == 'NOW':
            dt_now = super().utcnow()
            hour, minute, second, microsecond = dt_now.hour, dt_now.minute, dt_now.second, dt_now.microsecond
        elif force_time == 'FIRST_MINUTE':
            hour, minute, second, microsecond = 0, 0, 0, 0
        elif force_time == 'LAST_MINUTE':
            hour, minute, second, microsecond = 23, 59, 59, 999999
        else:
            raise ValueError("Invalid force_time. Please choose one of the following: NOW, MIDDAY, FIRST_MINUTE, LAST_MINUTE.")

        return self.replace(hour=hour, minute=minute, second=second, microsecond=microsecond)

    # OLD string_to_date_time
    @classmethod
    def strptime(cls, date_string: str, format: str = date_settings.DEFAULT_DATE_TIME_FORMAT) -> Self: # pylint: disable=redefined-builtin
        """
        Parse a string representing a date and time into a DateTime object.

        This class method parses a string `date_string` representing a date and time according to the provided
        format string `format` and returns a DateTime object.

        Args:
            date_string (str): The input date and time string to parse.
            format (str, optional): The format string specifying the expected format of `date_string`.
                - Defaults to the format '%Y%m%d %H:%M:%S'.

        Raises:
            ValueError: If the input `date_string` does not match the provided `format` format.

        Returns:
            DateTime: A DateTime object representing the parsed date and time.

        Example:
            Parse a date and time string into a DateTime object:
            >>> date_string = '2023-09-15 12:00:00'
            >>> DateTime.strptime(date_string, format='%Y-%m-%d %H:%M:%S')
            DateTime(2023, 9, 15, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))
        """
        return super().strptime(date_string, format)

    @classmethod
    def strptime_or_null(cls, date_string: str, format: str = date_settings.DEFAULT_DATE_TIME_FORMAT) -> Union[Self, None]: # pylint: disable=redefined-builtin
        """
        Parse a string representing a date and time into a DateTime object, or return None if parsing fails.

        This class method attempts to parse a string `date_string` representing a date and time according to
        the provided format string `format` and returns a DateTime object. If parsing fails, it returns None.

        Args:
            date_string (str): The input date and time string to parse.
            format (str, optional): The format string specifying the expected format of `date_string`.
                - Defaults to the format specified in `date_settings.DEFAULT_DATE_TIME_FORMAT`.

        Returns:
            DateTime or None: A DateTime object representing the parsed date and time, or None if parsing fails.

        Example:
            Parse a date and time string into a DateTime object or return None if parsing fails:
            >>> date_string = '2023-09-15 12:00:00'
            >>> DateTime.strptime_or_null(date_string, format='%Y-%m-%d %H:%M:%S')
            DateTime(2023, 9, 15, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))

            >>> invalid_date_string = '2023-09-15T12:00:00Z'
            >>> DateTime.strptime_or_null(invalid_date_string)
            None
        """
        date_time = None

        try:
            date_time = cls.strptime(date_string, format=format)
        except Exception: # pylint: disable=broad-exception-caught
            pass

        return date_time

    # OLD string_date_to_date_time
    @classmethod
    def string_date_to_date_time(cls, date_string: str, force_time: str = date_settings.DEFAULT_FORCE_TIME) -> Self:
        """
        Convert a string date to a DateTime object with a specified time.

        This class method converts a given string date to a DateTime object
        by combining the provided date string with a specified time. The `force_time`
        parameter allows you to set the time component of the resulting datetime object.
        If no `force_time` is provided, the default time is used.

        Args:
            date_string (str): A string representing a date.
            force_time (str, optional): A string indicating the desired time for the datetime object.
                Valid values are 'MIDDAY', 'NOW', 'FIRST_MINUTE', 'LAST_MINUTE', or a custom time in the format 'HH:MM:SS'. Defaults to 'MIDDAY'.

        Raises:
            ValueError: If an invalid `force_time` value is provided.

        Returns:
            DateTime: A DateTime object representing the combination of the input string date and the specified or default time.

        Example:
            Convert a string date to a datetime object with a specified time:
            >>> DateTime.string_date_to_date_time('20230815', force_time='MIDDAY')
            DateTime(2023, 8, 15, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))

            >>> DateTime.string_date_to_date_time('20230815', force_time='FIRST_MINUTE')
            DateTime(2023, 8, 15, 0, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))

            >>> DateTime.string_date_to_date_time('20230815')
            DateTime(2023, 8, 15, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))  # Assuming DEFAULT_FORCE_TIME is 'MIDDAY'
        """
        if force_time == 'MIDDAY':
            force_time = '12:00:00'
        elif force_time == 'NOW':
            force_time = super().utcnow().strftime('%H:%M:%S')
        elif force_time == 'FIRST_MINUTE':
            force_time = '00:00:00'
        elif force_time == 'LAST_MINUTE':
            force_time = '23:59:59'
        return super().strptime(f'{date_string} {force_time}', date_settings.DEFAULT_DATE_TIME_FORMAT)

    def strftime(self, format: str = date_settings.DEFAULT_DATE_TIME_FORMAT) -> str: # pylint: disable=redefined-builtin, useless-parent-delegation
        """
        Convert a DateTime object to a date string.

        This method takes a DateTime object and converts it to a date string using the specified date format.
        If no format is provided, the method will use the default date format specified in `date_settings.DEFAULT_DATE_TIME_FORMAT`.

        Args:
            format (str, optional): The desired date format. This should be a string representing the desired format using the appropriate format codes. Defaults to '%Y%m%d %H:%M:%S'.

        Raises:
            ValueError: If the provided `format` format string is invalid.

        Returns:
            str: The date string representation of the DateTime object in the specified date format.

        Example:
            Convert a DateTime object to a date string:
            >>> dt = DateTime(2023, 9, 15, 12, 0)
            >>> dt.strftime('%Y-%m-%d %H:%M:%S')
            '2023-09-15 12:00:00'

            >>> dt.strftime('%d/%m/%Y %H:%M:%S')
            '15/09/2023 12:00:00'
        """
        return super().strftime(format)

    @classmethod
    def strftime_or_null(cls, datetime_: Any, format: str = date_settings.DEFAULT_DATE_TIME_FORMAT) -> Union[str, None]: # pylint: disable=redefined-builtin
        """
        Convert a `DateTime` object to a string representation or return None if the input is not a Date.

        This class method takes a `DateTime` object and converts it to a string representation
        using the specified date format. If the input date is None, the method returns None.

        Args:
            datetime_ (DateTime or None): The `DateTime` object to convert to a string representation, or None.
            format (str, optional): The desired date format. This should be a string representing the desired format using the appropriate format codes. Defaults to `date_settings.DEFAULT_DATE_TIME_FORMAT`.

        Raises:
            ValueError: If the provided `format` format string is invalid.

        Returns:
            str or None: A string representation of the input date in the specified date format, or None if the input date is None.

        Example:
            Convert a `DateTime` object to a string representation or return None:
            >>> date_obj = DateTime(2023, 7, 31, 12, 0)
            >>> DateTime.strftime_or_null(date_obj)
            '20230731 12:00:00'

            >>> DateTime.strftime_or_null(None)
            None
        """
        if datetime_ is not None:
            try:
                datetime_ = datetime_.strftime(format=format)
            except Exception: # pylint: disable=broad-exception-caught
                datetime_ = None

        return datetime_

    # OLD date_time_to_pretty
    def strftime_pretty(self, just_date: bool = False, just_time: bool = False) -> str:
        """
        Convert a DateTime object to a pretty date string representation.

        This method takes a DateTime object and converts it to a pretty date string
        representation with an optional time zone adjustment. The date string representation follows
        the format 'Month day, Year' if `just_time` is False, and 'Month day, Year, Hour:Minute:Second AM/PM'
        if `just_time` is True.

        Args:
            just_date (bool, optional):
                If True, the hour information is omitted and only the date is shown.
                If False, the full date and time are shown.
                - Defaults to False.
            just_time (bool, optional):
                If True, the date information is omitted and only the time is shown.
                If False, the full date and time are shown.
                - Defaults to False.

        Raises:
            ValueError: If an invalid value is provided for the `just_time` or `just_date` parameter.

        Returns:
            str:
                A pretty date or time string representation of the input DateTime object.

        Criteria:
            - The method accepts an input `just_date` and  `just_time` parameter to control the display of date and time.
            - It raises a ValueError if an invalid value is provided for the `just_time` or `just_date`parameter.
            - It returns a string representing the DateTime object in a pretty format.

        Example:
            Convert a DateTime object to a pretty date string representation:
            >>> date_time_obj = DateTime(2023, 7, 31, 12, 34, 56)
            >>> DateTime.strftime_pretty(date_time_obj)
            'Jul. 31, 2023, 12:34:56 p.m.'

            >>> DateTime.strftime_pretty(date_time_obj, just_time=True)
            '12:34 p.m.'

            >>> DateTime.strftime_pretty(date_time_obj, just_date=True)
            'Jul. 31, 2023'
        """
        if just_date and just_time:
            raise ValueError('Both "just_date" and "just_time" flags cannot be true')

        out = None
        if just_date:
            out = self.strftime('%b. %d, %Y')
        elif just_time:
            out = self.strftime('%I:%M %p')
        else:
            out = self.strftime('%b. %d, %Y, %I:%M:%S %p')
        out = out.replace('PM', 'p.m.')
        out = out.replace('AM', 'a.m.')
        return out

    @classmethod
    def date_to_date_time(cls, date_: 'Date', frc_time: str = date_settings.DEFAULT_FORCE_TIME) -> Self: # type: ignore
        """
        Convert a Date object to a DateTime object.

        This class method takes a Date object and converts it to a DateTime
        object by combining the specified `date` with the provided `frc_time`, creating a combined
        date and time representation.

        Args:
            date_ (Date): The Date object to convert to a DateTime object.
            frc_time (str, optional):
                The time to append to the date. This should be a valid time representation
                compatible with the DateTime.strptime function.
                - Defaults to DEFAULT_FORCE_TIME = 'MIDDAY', which sets the time to 12:00:00.

        Raises:
            ValueError: If an invalid value is provided for the `frc_time` parameter.

        Returns:
            DateTime:
                A DateTime object representing the date and time
                obtained by combining the input date with the specified `frc_time`.

        Criteria:
            - The method accepts a `Date` object as input and converts it to a `DateTime` object.
            - It raises a ValueError if an invalid value is provided for the `frc_time` parameter.
            - It returns a `DateTime` object representing the combined date and time.

        Examples:
            >>> date_obj = Date(2023, 7, 31)
            >>> DateTime.date_to_date_time(date_obj)
            DateTime(2023, 7, 31, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))

            >>> date_obj = Date(2023, 1, 1)
            >>> DateTime.date_to_date_time(date_obj, frc_time='MIDDAY')
            DateTime(2023, 1, 1, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))
        """
        # string_date = date_.strftime('%Y-%m-%d')
        # date_time_str = f'{string_date} {frc_time}'
        return DateTime(date_.year, date_.month, date_.day).force_time(force_time=frc_time)

    @staticmethod
    def is_datetime(value: Any) -> bool:
        """
        Check if a value is a DateTime object.

        This static method checks whether a given value is an instance of the `DateTime` class or the built-in `datetime.datetime` class.
        It's necessary to use this custom check because `isinstance(value, date)` will return True for both `datetime` and `date` objects
        due to their shared base class.

        Args:
            value (Any): The value to be checked.

        Returns:
            bool: True if the value is a DateTime object, False otherwise.

        Criteria:
            - The method checks if the value is an instance of the `DateTime` class or `datetime.datetime` class.
            - It returns True if the value is a DateTime object, otherwise False.

        Example:
            Check if a value is a DateTime object:
            >>> value = DateTime(2023, 7, 31, 12, 34, 56)
            >>> DateTime.is_datetime(value)
            True

            >>> value = datetime.datetime(2023, 7, 31, 12, 34, 56)
            >>> DateTime.is_datetime(value)
            True

            >>> value = Date(2023, 7, 31)
            >>> DateTime.is_datetime(value)
            False
        """
        if value is not None:
            if value.__class__ in (DateTime, datetime):
                return True

        return False

    # OLD is_realtime_portfolio_date
    def is_today(self) -> bool:
        """
        Check if the DateTime object corresponds to the current date.

        This method compares the DateTime object with the current date and returns True if they represent the same date.

        Returns:
            bool: True if the DateTime object represents the current date, False otherwise.

        Criteria:
            - The method compares the DateTime object with the current date.
            - It returns True if they represent the same date, otherwise False.

        Example:
            Check if a DateTime object corresponds to the current date:
            >>> date_time_obj = DateTime(2023, 1, 1)
            >>> date_time_obj.is_today()
            False

            >>> current_date_time = DateTime.now()
            >>> current_date_time.is_today()
            True
        """
        return DateTime.now().date() == self.date()
