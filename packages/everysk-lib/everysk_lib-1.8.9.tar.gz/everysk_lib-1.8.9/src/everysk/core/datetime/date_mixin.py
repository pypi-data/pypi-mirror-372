
###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from calendar import monthrange, SATURDAY, SUNDAY
from datetime import datetime, date, timedelta
from typing import Union, Self, TYPE_CHECKING

from everysk.core.datetime import date_settings

if TYPE_CHECKING:
    from everysk.core.datetime import Date, DateTime


def get_holidays(calendar: str, years: list = Undefined) -> dict:
    """
    Uses https://pypi.org/project/holidays/ to make a list of dates.
    Pass a list of years if you need a more specific list.

    Args:
        calendar (str): Two digit country symbol.
        years (list, optional): List of int years. Ex: [2021, 2022]. Defaults to Undefined.

    Returns:
        dict: A dictionary containing holiday dates as keys and holiday names as values.

    Example:
        >>> from everysk.core.datetime.date_mixin import get_holidays
        >>> br_holidays = get_holidays('BR', years=[2021, 2022])
        >>> print(brazil_holidays)
        {
            datetime.date(2021, 1, 1): 'Confraternização Universal',
            datetime.date(2023, 4, 2): 'Sexta-feira Santa',
            ...
        }
    """
    if calendar:
        kwargs = {'calendar': calendar}

        if years is not Undefined:
            kwargs['years'] = years

        # This module has 10 mb so we only import it when needed
        from everysk.core.datetime import calendar # pylint: disable=import-outside-toplevel
        return calendar.get_holidays(**kwargs)

    return {}


class DateMixin:

    @property
    def quarter(self) -> int:
        """
        Get the quarter of the year for the current date.

        Returns:
            int: The quarter of the year (1 to 4) for the current date.

        Example:
            >>> date_obj = Date(2023, 7, 31)
            >>> date_obj.quarter
            3

            >>> date_time_obj = DateTime(2023, 7, 31, 12, 0)
            >>> date_time_obj.quarter
            3
        """
        return (self.month - 1) // 3 + 1

    @property
    def month_name(self) -> str:
        """
        Get the name of the month for the current date.

        Returns:
            str: The name of the month for the current date.

        Example:
            >>> date_obj = Date(2023, 7, 31)
            >>> date_obj.month_name
            'July'

            >>> date_time_obj = DateTime(2023, 7, 31, 12, 0)
            >>> date_time_obj.month_name
            'July'
        """
        return self.strftime('%B')

    @property
    def week_of_year(self) -> int:
        """
        Get the week of the year for the current date.

        Returns:
            int: The week of the year (0 to 53) for the current date.

        Example:
            >>> date_obj = Date(2023, 7, 31)
            >>> date_obj.week_of_year
            31  # Represents the 30th week of the year.

            >>> date_time_obj = DateTime(2023, 7, 31, 12, 0)
            >>> date_time_obj.week_of_year
            31
        """
        return int(self.strftime('%U'))

    @property
    def week_of_month(self) -> int:
        """
        Get the week of the month for the current date.

        Returns:
            int: The week of the month (1 to 5) for the current date.

        Example:
            >>> date_obj = Date(2023, 7, 31)
            >>> date_obj.week_of_month
            5  # Represents the fifth week of the month.

            >>> date_time_obj = DateTime(2023, 7, 31, 12, 0)
            >>> date_time_obj.week_of_month
            5
        """
        return (self.day - 1) // 7 + 1

    @property
    def day_name(self) -> str:
        """
        Get the name of the day of the week for the current date.

        Returns:
            str: The name of the day of the week for the current date.

        Example:
            >>> date_obj = Date(2023, 7, 31)
            >>> date_obj.day_name
            'Sunday'

            >>> date_obj = DateTime(2023, 7, 31, 12, 00)
            >>> date_obj.day_name
            'Sunday'
        """
        return self.strftime('%A')

    @property
    def day_of_year(self) -> int:
        """
        Get the day of the year for the current date.

        Returns:
            int: The day of the year (1 to 366) for the current date.

        Example:
            >>> date_obj = Date(2023, 7, 31)
            >>> date_obj.day_of_year
            212  # Represents the 212th day of the year.

            >>> date_obj = DateTime(2023, 7, 31, 12, 00)
            >>> date_obj.day_of_year
            212
        """
        return self.timetuple().tm_yday

    def toordinal(self, start_date: Union['Date', 'DateTime'] = None) -> int:
        """
        Get the ordinal day count since a base date for the current date.

        This method returns the ordinal day count since a specified `start_date` for the current date.
        If `start_date` is provided, the day count is calculated relative to that date; otherwise, it's calculated
        relative to the base date '00010101'.

        Args:
            start_date (Date or DateTime, optional): The base date for calculating the ordinal day count. Defaults to None.

        Raises:
            AttributeError: When the start date is not a Date, DateTime or None.

        Returns:
            int: The ordinal day count since the specified `start_date` or the base date '00010101'.

        Example:
            >>> date_obj = Date(2023, 7, 31)
            >>> date_obj.toordinal()
            738732  # Represents the ordinal day count since '00010101'.

            >>> base_date = DateTime(2000, 1, 1, 12, 0)
            >>> date_obj = DateTime(2023, 7, 31, 12, 0)
            >>> date_obj.toordinal(start_date=base_date)
            8613  # Represents the ordinal day count since '20000101'.
        """
        delta = 0

        # pylint: disable=not-callable
        if start_date:
            start_date = date(start_date.year, start_date.month, start_date.day)
            delta = start_date.toordinal() - 1

        result = date(self.year, self.month, self.day).toordinal() - delta
        return result

    ####################################
    ### HELPERS
    ####################################

    @classmethod
    def market_start(cls) -> Self:
        """
        This class method returns the market start date, which is the date when the market opens for the first time.

        Returns:
            Date or DateTime: The market start date.

        Example:
            >>> Date.market_start()
            Date(2023, 7, 1)

            >>> DateTime.market_start()
            DateTime(2023, 7, 1, 0, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))
        """
        return cls.ensure(date_settings.MARKET_START_DATE_TIME)

    @staticmethod
    def _adjust_direction(start_date: Union['Date', 'DateTime'], end_date: Union['Date', 'DateTime']) -> tuple[Union['Date', 'DateTime'], Union['Date', 'DateTime'], int]:
        """
        Adjust the start and end dates and calculate a multiplier if necessary.

        This static method takes two dates, `start_date` and `end_date`, and adjusts them if `end_date` is earlier than `start_date`.
        It also calculates a multiplier to adjust the calculation direction if needed.

        Args:
            start_date (Union['Date', 'DateTime']): The start date of the date range.
            end_date (Union['Date', 'DateTime']): The end date of the date range.

        Returns:
            tuple[Union['Date', 'DateTime'], Union['Date', 'DateTime'], int]: A tuple containing the adjusted `start_date`, `end_date`, and a direction (1 or -1).

       Example:
            >>> start = DateTime(2023, 7, 1)
            >>> end = DateTime(2023, 6, 1)
            >>> DateTime._adjust_direction(start, end)
            (DateTime(2023, 6, 1, 0, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC')),
             DateTime(2023, 7, 1, 0, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC')),
             -1)

            >>> start = Date(2023, 7, 1)
            >>> end = Date(2023, 6, 1)
            >>> Date._adjust_direction(start, end)
            (Date(2023, 6, 1), Date(2023, 7, 1), -1)
        """
        direction = 1

        if end_date < start_date:
            end_date, start_date = start_date, end_date
            direction = -1

        return (start_date, end_date, direction)

    ####################################
    ### GET LAST DATE OF
    ####################################

    def get_last_day_of_week(self, bizdays: bool = False, calendar: str = None) -> Self:
        """
        Get the last day of the week for a given date, optionally considering business days and holidays.

        This method calculates the last day of the week (Saturday) for the current date or the provided 'Date' or 'DateTime' object.
        Optionally, it can also consider business days by excluding weekends and accounting for holidays.

        Args:
            bizdays (bool, optional): If True, consider business days by excluding Weekends. Defaults to False.
            calendar (str, optional): A calendar name used to determine holidays. Defaults to None, which means no holidays are considered.

        Raises:
            NotImplementedError: If an invalid `calendar` name is provided.

        Returns:
            Date or DateTime: The last day of the week (Sunday) for the current date or the provided `Date` or `DateTime` object, considering business days and holidays if specified.

        Example:
            To calculate the last day of the week for the current date:
            >>> Date(2023, 8, 11).get_last_day_of_week()
            Date(2023, 8, 12)

            To calculate the last day of the week with business days and holidays using a specific calendar:
            >>> DateTime(2023, 8, 11, 12, 0).get_last_day_of_week(bizdays=True)
            DateTime(2023, 8, 11, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))
        """
        last_day = self

        while last_day.weekday() != SATURDAY:
            last_day += timedelta(days=1)

        if bizdays:
            last_day -= timedelta(days=1)

        if calendar:
            hdays = get_holidays(calendar, years=[self.year - 1, self.year, self.year + 1])

            while last_day.date() in hdays or (bizdays and last_day.weekday() in (SUNDAY, SATURDAY)):
                last_day -= timedelta(days=1)

        return last_day

    def get_last_day_of_month(self, bizdays: bool = False, calendar: str = None) -> Self:
        """
        Get the last day of the month for a given date, optionally considering business days and holidays.

        This method calculates the last day of the month for the current date or the provided `Date` or `DateTime` object.
        Optionally, it can also consider business days by excluding weekends and accounting for holidays.

        Args:
            bizdays (bool, optional): If True, consider business days by excluding weekends. Defaults to False.
            calendar (str, optional): A calendar name used to determine holidays. Defaults to None, which means no holidays are considered.

        Raises:
            NotImplementedError: If an invalid `calendar` name is provided.

        Returns:
            Date or DateTime: The last day of the month for the current date or the provided `Date` or `DateTime` object, considering business days and holidays if specified.

        Example:
            To calculate the last day of the month for the current date:
            >>> Date(2023, 8, 11).get_last_day_of_month()
            Date(2023, 8, 31)

            To calculate the last day of the month with business days and holidays using a specific calendar:
            >>> DateTime(2023, 8, 11, 12, 0).get_last_day_of_month(bizdays=True)
            DateTime(2023, 8, 31, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))
        """
        last_day = self

        day = monthrange(last_day.year, last_day.month)[1]
        last_day = last_day.replace(year=last_day.year, month=last_day.month, day=day)

        if bizdays:
            while last_day.weekday() in (SUNDAY, SATURDAY):
                last_day -= timedelta(days=1)

        if calendar:
            hdays = get_holidays(calendar, years=[self.year])

            while last_day.date() in hdays or (bizdays and last_day.weekday() in (SUNDAY, SATURDAY)):
                last_day -= timedelta(days=1)

        return last_day

    def get_last_day_of_quarter(self, bizdays: bool = False, calendar: str = None) -> Self:
        """
        Get the last day of the quarter for a given date, optionally considering business days and holidays.

        This method calculates the last day of the quarter for the current date or the provided `Date` or `DateTime` object.
        Optionally, it can also consider business days by excluding weekends and accounting for holidays.

        Args:
            bizdays (bool, optional): If True, consider business days by excluding weekends. Defaults to False.
            calendar (str, optional): A calendar name used to determine holidays. Defaults to None, which means no holidays are considered.

        Raises:
            NotImplementedError: If an invalid `calendar` name is provided.

        Returns:
            Date or DateTime: The last day of the quarter for the current date or the provided `Date` or `DateTime` object, considering business days and holidays if specified.

        Example:
            To calculate the last day of the quarter for the current date:
            >>> Date(2023, 8, 11).get_last_day_of_quarter()
            Date(2023, 9, 30)

            To calculate the last day of the quarter with business days and holidays using a specific calendar:
            >>> DateTime(2023, 8, 11, 12, 0).get_last_day_of_quarter(bizdays=True)
            DDateTime(2023, 9, 29, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))
        """
        current_quarter = (self.month - 1) // 3 + 1
        last_month_of_quarter = current_quarter * 3

        # To handle months with varying numbers of days, set the date to the first day of the last month of the quarter.
        # This prevents the month from being instantiated with an incorrect number of days
        new_date = self.replace(day=1, month=last_month_of_quarter)
        last_day = new_date.get_last_day_of_month(bizdays=bizdays, calendar=calendar)

        return last_day

    def get_last_day_of_year(self, bizdays: bool = False, calendar: str = None) -> Self:
        """
        Get the last day of the year for a given date, optionally considering business days and holidays.

        This method calculates the last day of the year for the current date or the provided Date or DateTime object.
        Optionally, it can also consider business days by excluding weekends and accounting for holidays.

        Args:
            bizdays (bool, optional): If True, consider business days by excluding weekends. Defaults to False.
            calendar (str, optional): A calendar name used to determine holidays. Defaults to None, which means no holidays are considered.

        Raises:
            ValueError: If an invalid `calendar` name is provided.

        Returns:
            Date or DateTime: The last day of the year for the current date or the provided Date or DateTime object, considering business days and holidays if specified.

        Example:
            To calculate the last day of the year for the current date:
            >>> Date(2023, 8, 11).get_last_day_of_year()
            Date(2023, 12, 31)

            To calculate the last day of the year with business days and holidays using a specific calendar:
            >>> DateTime(2023, 8, 11).get_last_day_of_year(bizdays=True)
            DateTime(2023, 12, 29, 0, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))
        """
        last_day = self.replace(month=12)

        last_day = last_day.get_last_day_of_month(bizdays=bizdays, calendar=calendar)

        return last_day

    ####################################
    ### IS LAST DATE OF
    ####################################

    def is_last_day_of_week(self, bizdays: bool = False, calendar: str = None) -> bool:
        """
        Check if a given date is the last day of the week, optionally considering business days and holidays.

        This method checks if the input date is the last day of the week (Saturday).
        Optionally, it can also consider business days by excluding weekends and accounting for holidays.

        Args:
            bizdays (bool, optional): If True, consider business days by excluding Sundays. Defaults to False.
            calendar (str, optional): The name of the calendar to use for holiday calculation. If provided, holidays will be considered when checking for the last day of the week. Defaults to None.

        Raises:
            NotImplementedError: If an invalid `calendar` name is provided.

        Returns:
            bool: True if the input date is the last day of the week, considering business days and holidays if specified, False otherwise.

        Example:
            To check if a specific date is the last day of the week:
            >>> Date(2023, 8, 12).is_last_day_of_week()
            True

            To check if a date is the last day of the week with business days and holidays using a specific calendar:
            >>> DateTime(2023, 8, 11, 12, 0).is_last_day_of_week(bizdays=True)
            True
        """
        return self == self.get_last_day_of_week(bizdays=bizdays, calendar=calendar)

    def is_last_day_of_month(self, bizdays: bool = False, calendar: str = None) -> bool:
        """
        Check if a given date is the last day of the month, optionally considering business days and holidays.

        This method checks if the input date is the last day of the month.
        Optionally, it can also consider business days by excluding weekends and accounting for holidays.

        Args:
            bizdays (bool, optional): If True, consider business days by excluding weekends. Defaults to False.
            calendar (str, optional): The name of the calendar to use for holiday calculation. If provided, holidays will be considered when checking for the last day of the month. Defaults to None.

        Raises:
            NotImplementedError: If an invalid `calendar` name is provided.

        Returns:
            bool: True if the input date is the last day of the month, considering business days and holidays if specified, False otherwise.

        Example:
            To check if a specific date is the last day of the month:
            >>> Date(2023, 8, 31).is_last_day_of_month()
            True

            To check if a date is the last day of the month with business days and holidays using a specific calendar:
            >>> DateTime(2023, 8, 30, 12, 0).is_last_day_of_month(bizdays=True)
            False
        """
        return self == self.get_last_day_of_month(bizdays=bizdays, calendar=calendar)

    def is_last_day_of_quarter(self, bizdays: bool = False, calendar: str = None) -> bool:
        """
        Check if a given date is the last day of the quarter, optionally considering business days and holidays.

        This method checks if the input date is the last day of the quarter.
        Optionally, it can also consider business days by excluding weekends and accounting for holidays.

        Args:
            bizdays (bool, optional): If True, consider business days by excluding weekends. Defaults to False.
            calendar (str, optional): The name of the calendar to use for holiday calculation. If provided, holidays will be considered when checking for the last day of the quarter. Defaults to None.

        Raises:
            NotImplementedError: If an invalid `calendar` name is provided.

        Returns:
            bool: True if the input date is the last day of the quarter, considering business days and holidays if specified, False otherwise.

        Example:
            To check if a specific date is the last day of the quarter:
            >>> Date(2023, 9, 30).is_last_day_of_quarter()
            True

            To check if a date is the last day of the quarter with business days and holidays using a specific calendar:
            >>> DateTime(2023, 9, 29, 12, 0).is_last_day_of_quarter(bizdays=True)
            True
        """
        return self == self.get_last_day_of_quarter(bizdays=bizdays, calendar=calendar)

    def is_last_day_of_year(self, bizdays: bool = False, calendar: str = None) -> bool:
        """
        Check if a given date is the last day of the year, optionally considering business days and holidays.

        This method checks if the input date is the last day of the year.
        Optionally, it can also consider business days by excluding weekends and accounting for holidays.

        Args:
            bizdays (bool, optional): If True, consider business days by excluding weekends. Defaults to False.
            calendar (str, optional): The name of the calendar to use for holiday calculation. If provided, holidays will be considered when checking for the last day of the year. Defaults to None.

        Raises:
            NotImplementedError: If an invalid `calendar` name is provided.

        Returns:
            bool: True if the input date is the last day of the year, considering business days and holidays if specified, False otherwise.

        Example:
            To check if a specific date is the last day of the year:
            >>> Date(2023, 12, 31).is_last_day_of_year()
            True

            To check if a date is the last day of the year with business days and holidays using a specific calendar:
            >>> DateTime(2023, 12, 30, 12, 0).is_last_day_of_year(bizdays=True)
            False
        """
        return self == self.get_last_day_of_year(bizdays=bizdays, calendar=calendar)

    ####################################
    ### GET FIRST DATE OF
    ####################################

    def get_first_day_of_week(self, bizdays: bool = False, calendar: str = None) -> Self:
        """
        Get the first day of the week for a given date, optionally considering business days and holidays.

        This static method takes a Date or DateTime object and calculates the first day of the week (Sunday) for that week.
        Optionally, it can also consider business days by excluding weekends and accounting for holidays.

        Args:
            bizdays (bool, optional): If True, consider business days by excluding weekends. Defaults to False.
            calendar (str, optional): The name of the calendar to use for holiday calculation. If provided, holidays will be considered when checking for the last day of the year. Defaults to None.

        Raises:
            NotImplementedError: If an invalid `calendar` name is provided.

        Returns:
            Date or DateTime: The first day of the week (Sunday) for the input date, considering business days and holidays if specified.

        Example:
            To check if a specific date is the first day of the week:
            >>> Date(2023, 8, 11).get_first_day_of_week()
            Date(2023, 8, 6)

            To calculate the first day of the week with business days and holidays using a specific calendar:
            >>> DateTime(2023, 8, 11, 12, 0).get_first_day_of_week(bizdays=True)
            DateTime(2023, 8, 7, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))
        """
        first_day = self

        while first_day.weekday() != SUNDAY:
            first_day -= timedelta(days=1)

        if bizdays:
            first_day += timedelta(days=1)

        if calendar:
            hdays = get_holidays(calendar, years=[self.year - 1, self.year, self.year + 1])

            while first_day.date() in hdays or (bizdays and first_day.weekday() in (SUNDAY, SATURDAY)):
                first_day += timedelta(days=1)

        return first_day

    def get_first_day_of_month(self, bizdays: bool = False, calendar: str = None) -> Self:
        """
        Get the first day of the month for a given date, optionally considering business days and holidays.

        This static method takes a Date or DateTime object and calculates the first day of the month for that date.
        Optionally, it can also consider business days by excluding weekends and accounting for holidays.

        Args:
            bizdays (bool, optional): If True, consider business days by excluding weekends. Defaults to False.
            calendar (str, optional): The name of the calendar to use for holiday calculation. If provided, holidays will be considered when checking for the last day of the year. Defaults to None.

        Raises:
            NotImplementedError: If an invalid `calendar` name is provided.

        Returns:
            Date or DateTime: The first day of the month for the input date, considering business days and holidays if specified.

        Example:
            To check if a specific date is the first day of the month:
            >>> Date(2023, 8, 11).get_first_day_of_month()
            Date(2023, 8, 1)

            To calculate the first day of the month with business days and holidays using a specific calendar:
            >>> DateTime(2023, 8, 11, 12, 0).get_first_day_of_month(bizdays=True)
            DateTime(2023, 8, 1, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))
        """
        first_day = self.replace(day=1)

        if bizdays:
            while first_day.weekday() in (SUNDAY, SATURDAY):
                first_day += timedelta(days=1)

        if calendar:
            hdays = get_holidays(calendar, years=[self.year])

            while first_day.date() in hdays or (bizdays and first_day.weekday() in (SUNDAY, SATURDAY)):
                first_day += timedelta(days=1)

        return first_day

    def get_first_day_of_quarter(self, bizdays: bool = False, calendar: str = None) -> Self:
        """
        Get the first day of the quarter for a given date, optionally considering business days and holidays.

        This static method takes a Date or DateTime object and calculates the first day of the quarter for that date.
        Optionally, it can also consider business days by excluding weekends and accounting for holidays.

        Args:
            bizdays (bool, optional): If True, consider business days by excluding weekends. Defaults to False.
            calendar (str, optional): The name of the calendar to use for holiday calculation. If provided, holidays will be considered when checking for the last day of the year. Defaults to None.

        Raises:
            NotImplementedError: If an invalid `calendar` name is provided.

        Returns:
            Date or DateTime: The first day of the quarter for the input date, considering business days and holidays if specified.

        Example:
            To check if a specific date is the first day of the quarter:
            >>> Date(2023, 8, 11).get_first_day_of_quarter()
            Date(2023, 7, 1)

            To calculate the first day of the quarter with business days and holidays using a specific calendar:
            >>> DateTime(2023, 8, 11, 12, 0).get_first_day_of_quarter(bizdays=True)
            DateTime(2023, 7, 3, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))
        """
        first_month_of_quarter = (self.quarter - 1) * 3 + 1

        first_day = self.replace(month=first_month_of_quarter, day=1)

        first_day = first_day.get_first_day_of_month(bizdays=bizdays, calendar=calendar)

        return first_day

    def get_first_day_of_year(self, bizdays: bool = False, calendar: str = None) -> Self:
        """
        Get the first day of the year for a given date, optionally considering business days and holidays.

        This static method takes a Date or DateTime object and calculates the first day of the year for that date.
        Optionally, it can also consider business days by excluding weekends and accounting for holidays.

        Args:
            bizdays (bool, optional): If True, consider business days by excluding weekends. Defaults to False.
            calendar (str, optional): The name of the calendar to use for holiday calculation. If provided, holidays will be considered when checking for the last day of the year. Defaults to None.

        Raises:
            NotImplementedError: If an invalid `calendar` name is provided.

        Returns:
            Date or DateTime: The first day of the year for the input date, considering business days and holidays if specified.

        Example:
            To check if a specific date is the first day of the year:
            >>> Date(2023, 8, 11).get_first_day_of_year()
            Date(2023, 1, 1)

            To calculate the first day of the year with business days and holidays using a specific calendar:
            >>> DateTime(2023, 8, 11, 12, 0).get_first_day_of_year(bizdays=True)
            DateTime(2023, 1, 2, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))
        """
        first_day = self.replace(month=1, day=1)

        first_day = first_day.get_first_day_of_month(bizdays=bizdays, calendar=calendar)

        return first_day

    ####################################
    ### IS FIRST DATE OF
    ####################################

    def is_first_day_of_week(self, bizdays: bool = False, calendar: str = None) -> bool:
        """
        Check if a provided date corresponds to the first day of the week, optionally considering business days and holidays.

        This method compares the provided `Date` or `DateTime` object with the first day of the week (Sunday) and returns True if they are the same.
        Optionally, it can also consider business days by excluding weekends and accounting for holidays.

        Args:
            bizdays (bool, optional): If True, consider business days by excluding weekends. Defaults to False.
            calendar (str, optional): The name of the calendar to use for holiday calculation. If provided, holidays will be considered when checking for the last day of the year. Defaults to None.

        Raises:
            NotImplementedError: If an invalid `calendar` name is provided.

        Returns:
            bool: True if the `Date or DateTime` is the same as the first day of the week, False otherwise.

        Example:
            To check if a specific date is the first day of the week:
            >>> Date(2023, 8, 13).is_first_day_of_week()
            True

            To check if the current date is the first day of the week with business days and holidays using a specific calendar:
            >>> DateTime(2023, 8, 13, 12, 0).is_first_day_of_week(bizdays=True)
            False
        """
        return self == self.get_first_day_of_week(bizdays=bizdays, calendar=calendar)

    def is_first_day_of_month(self, bizdays: bool = False, calendar: str = None) -> bool:
        """
        Check if a provided date corresponds to the first day of the month, optionally considering business days and holidays.

        This method compares the provided `Date` or `DateTime` object with the first day of the month and returns True if they are the same.
        Optionally, it can also consider business days by excluding weekends and accounting for holidays.

        Args:
            bizdays (bool, optional): If True, consider business days by excluding weekends. Defaults to False.
            calendar (str, optional): The name of the calendar to use for holiday calculation. If provided, holidays will be considered when checking for the last day of the year. Defaults to None.

        Raises:
            NotImplementedError: If an invalid `calendar` name is provided.

        Returns:
            bool: True if the `Date or DateTime` is the same as the first day of the month, False otherwise.

        Example:
            To check if a specific date is the first day of the month:
            >>> Date(2023, 8, 1).is_first_day_of_month()
            True

            To check if the current date is the first day of the month with business days and holidays using a specific calendar:
            >>> DateTime(2023, 8, 1, 12, 0).is_first_day_of_month(bizdays=True)
            True
        """
        return self == self.get_first_day_of_month(bizdays=bizdays, calendar=calendar)

    def is_first_day_of_quarter(self, bizdays: bool = False, calendar: str = None) -> bool:
        """
        Check if a provided date corresponds to the first day of the quarter, optionally considering business days and holidays.

        This method compares the provided `Date` or `DateTime` object with the first day of the quarter and returns True if they are the same.
        Optionally, it can also consider business days by excluding weekends and accounting for holidays.

        Args:
            bizdays (bool, optional): If True, consider business days by excluding weekends. Defaults to False.
            calendar (str, optional): The name of the calendar to use for holiday calculation. If provided, holidays will be considered when checking for the last day of the year. Defaults to None.

        Raises:
            NotImplementedError: If an invalid `calendar` name is provided.

        Returns:
            bool: True if the `Date or DateTime` is the same as the first day of the quarter, False otherwise.

        Example:
            To check if a specific date is the first day of the quarter:
            >>> Date(2023, 7, 1).is_first_day_of_quarter()
            True

            To check if the current date is the first day of the quarter with business days and holidays using a specific calendar:
            >>> DateTime(2023, 7, 1, 12, 0).is_first_day_of_quarter(bizdays=True)
            True
        """
        return self == self.get_first_day_of_quarter(bizdays=bizdays, calendar=calendar)

    def is_first_day_of_year(self, bizdays: bool = False, calendar: str = None) -> bool:
        """
        Check if a provided date corresponds to the first day of the year, optionally considering business days and holidays.

        This method compares the provided `Date` or `DateTime` object with the first day of the year and returns True if they are the same.
        Optionally, it can also consider business days by excluding weekends and accounting for holidays.

        Args:
            bizdays (bool, optional): If True, consider business days by excluding weekends. Defaults to False.
            calendar (str, optional): The name of the calendar to use for holiday calculation. If provided, holidays will be considered when checking for the last day of the year. Defaults to None.

        Raises:
            NotImplementedError: If an invalid `calendar` name is provided.

        Returns:
            bool: True if the `Date or DateTime` is the same as the first day of the year, False otherwise.

        Example:
            To check if a specific date is the first day of the year:
            >>> Date(2023, 1, 1).is_first_day_of_year()
            True

            To check if the current date is the first day of the year with business days and holidays using a specific calendar:
            >>> DateTime(2023, 1, 1, 12, 0).is_first_day_of_year(bizdays=True)
            False
        """
        return self == self.get_first_day_of_year(bizdays=bizdays, calendar=calendar)

    ####################################
    ### DATE DELTA
    ####################################

    def delta(self, period: int | float, periodicity: str = 'D', calendar: str = None) -> Self:
        """
        Calculate a new Date or DateTime object by adding or subtracting a specified time period.

        This method calculates a new Date or DateTime object by adding or subtracting a specified time period based on the given periodicity.
        The valid periodicity options are 'D' (days), 'B' (business days), 'W' (weeks), 'M' (months), and 'Y' (years).
        It can also consider holidays based on the provided holiday calendar.

        Args:
            period (int | float): The number of time periods to add or subtract. A positive value adds, and a negative value subtracts.
            periodicity (str, optional): The periodicity of the time period. Valid options are 'D' (days), 'B' (business days), 'W' (weeks), 'M' (months), and 'Y' (years). Defaults to 'D'.
            calendar (str, optional): The name of the holiday calendar to use for considering holidays. Defaults to None.

        Raises:
            ValueError: If an invalid periodicity is provided.

        Returns:
            Date or DateTime: A new Date or DateTime object resulting from the addition or subtraction of the specified time period.

        Example:
            To calculate a new Date by adding 7 days:
            >>> Date(2023, 7, 1).delta(7, periodicity='D')
            Date(2023, 7, 8)

            To calculate a new DateTime by subtracting 3 business days using a specific calendar:
            >>> DateTime(2023, 7, 1, 12, 0).delta(-3, periodicity='B')
            DateTime(2023, 6, 28, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC')
        """
        new_date = None

        if periodicity == 'D':
            new_date = self.days_delta(period)
        elif periodicity == 'B':
            new_date = self.bizdays_delta(period, calendar=calendar)
        elif periodicity == 'W':
            new_date = self.weeks_delta(period)
        elif periodicity == 'M':
            new_date = self.months_delta(period)
        elif periodicity == 'Y':
            new_date = self.years_delta(period)
        else:
            raise ValueError("Invalid periodicity. Please choose one of the following: D, B, W, M, Y.")

        return new_date

    def days_delta(self, days: int | float) -> Self:
        """
        Calculate a new Date or DateTime object by adding or subtracting a specified number of days.

        This method calculates a new Date or DateTime object by adding or subtracting a specified number of days.

        Args:
            days (int | float): The number of days to add or subtract. A positive value adds, and a negative value subtracts.

        Raises:
            ValueError: If the input value `days` is greater than 50,000, indicating it's out of the valid range.

        Returns:
            Date or DateTime: A new Date or DateTime object resulting from the addition or subtraction of the specified number of days.

        Example:
            To calculate a new Date by adding 7 days:
            >>> Date(2023, 7, 1).days_delta(7)
            Date(2023, 7, 8)

            To calculate a new DateTime by subtracting 3 days:
            >>> DateTime(2023, 7, 1, 12, 0).days_delta(-3)
            DateTime(2023, 6, 28, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))
        """
        if days > date_settings.MAX_DAYS_RANGE:
            raise ValueError('Value out of range')

        new_date = self + timedelta(days=days)
        return new_date

    def bizdays_delta(self, bizdays: int | float, calendar: str = None) -> Self:
        """
        Calculate a new Date or DateTime object by adding or subtracting a specified number of business days.

        This method calculates a new Date or DateTime object by adding or subtracting a specified number of business days.
        Business days exclude weekends (Saturdays and Sundays) and optionally specified holidays based on the provided calendar.

        Args:
            bizdays (int | float): The number of business days to add or subtract. A positive value adds, and a negative value subtracts.
            calendar (str, optional): An optional calendar name specifying holidays to be considered when calculating business days. Defaults to None (no holiday consideration).

        Returns:
            Date or DateTime: A new Date or DateTime object resulting from the addition or subtraction of the specified number of business days.

        Example:
            To calculate a new Date by adding 5 business days:
            >>> Date(2023, 7, 1).bizdays_delta(5)
            Date(2023, 7, 7)

            To calculate a new DateTime by subtracting 3 business days with a specific calendar:
            >>> DateTime(2023, 7, 1, 12, 0).bizdays_delta(-3)
            DateTime(2023, 6, 28, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))
        """
        direction = 1 if bizdays >= 0 else -1
        bizdays = abs(bizdays)

        if bizdays > date_settings.MAX_DAYS_RANGE:
            raise ValueError('Value out of range')

        count = 0
        new_date = self

        hdays = get_holidays(calendar)

        while count < bizdays:
            new_date += timedelta(days=direction)
            if new_date.weekday() not in (SATURDAY, SUNDAY) and new_date.date() not in hdays:
                count += 1

        return new_date

    def weeks_delta(self, weeks: int | float) -> Self:
        """
        Calculate a new Date or DateTime object by adding or subtracting a specified number of weeks.

        This method calculates a new Date or DateTime object by adding or subtracting a specified number of weeks.

        Args:
            weeks (int | float): The number of weeks to add or subtract. A positive value adds, and a negative value subtracts.

        Returns:
            Date or DateTime: A new Date or DateTime object resulting from the addition or subtraction of the specified number of weeks.

        Example:
            To calculate a new Date by adding 3 weeks:
            >>> Date(2023, 7, 1).weeks_delta(3)
            Date(2023, 7, 22)

            To calculate a new DateTime by subtracting 2 weeks:
            >>> DateTime(2023, 7, 1, 12, 0).weeks_delta(-2)
            DateTime(2023, 6, 17, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))
        """
        new_date = self + timedelta(weeks=weeks)
        return new_date

    def months_delta(self, months: int) -> Self:
        """
        Calculate a new Date or DateTime object by adding or subtracting a specified number of months.

        This method calculates a new Date or DateTime object by adding or subtracting a specified number of months.
        The day of the resulting date is adjusted to ensure it remains valid within the month, considering leap years.

        Args:
            months (int): The number of months to add or subtract. A positive value adds, and a negative value subtracts.

        Returns:
            Date or DateTime: A new Date or DateTime object resulting from the addition or subtraction of the specified number of months.

        Example:
            To calculate a new Date by adding 3 months:
            >>> Date(2023, 7, 1).months_delta(3)
            Date(2023, 10, 1)

            To calculate a new DateTime by subtracting 2 months:
            >>> DateTime(2023, 7, 1, 12, 0).months_delta(-2)
            DateTime(2023, 5, 1, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))
        """
        months = int(months)

        month = self.month + months - 1
        year = self.year + month // 12
        month = month % 12 + 1

        days_of_month = monthrange(year, month)[1]
        day = min(self.day, days_of_month)

        end_date = self.replace(year=year, month=month, day=day)
        return end_date

    def years_delta(self, years: int) -> Self:
        """
        Calculate a new Date object by adding or subtracting a specified number of years.

        This method calculates a new Date object by adding or subtracting a specified number of years.
        It ensures that the day and month of the resulting date remain valid within the year, considering leap years.

        Args:
            years (int): The number of years to add or subtract. A positive value adds, and a negative value subtracts.

        Returns:
            Date or DateTime: A new Date or DateTime object resulting from the addition or subtraction of the specified number of years.

        Example:
            To calculate a new Date by adding 2 years:
            >>> Date(2023, 7, 15).years_delta(2)
            Date(2025, 7, 15)

            To calculate a new Date by subtracting 5 years:
            >>> Date(2023, 7, 15).years_delta(-5)
            Date(2018, 7, 15)
        """
        years = int(years)

        year = self.year + years
        month = self.month
        day = self.day

        days_of_month = monthrange(year, month)[1]
        day = min(self.day, days_of_month)

        end_date = self.replace(year=year, month=month, day=day)

        return end_date

    ####################################
    ### IS BUSINESS DAY
    ####################################

    def is_business_day(self, calendar: str = None)-> bool:
        """
        Checks if the date is a business day, considering weekends and optional holidays.

        Args:
            calendar (str, optional):
                The name of the calendar used to determine holidays.
                If None, only weekends are considered.

        Returns:
            bool:
                True if the date is a business day, False otherwise.
        """
        if self.weekday() in (SATURDAY, SUNDAY):
            return False

        hdays = get_holidays(calendar, [self.year])

        return not self.date() in hdays

    ####################################
    ### NEAREST BUSINESS DAY
    ####################################

    def nearest_business_day(self, direction: str = "following", calendar: str = None) -> Self:
        """
        Get the nearest business day for a given reference date, considering weekends and optional holidays.

        Args:
            reference_date (Date or DateTime):
                The date from which to find the nearest business day.
            direction (str):
                Determines whether to find the next ('following') or previous ('preceding') business day.
                Defaults to 'following'.
            calendar (str, optional):
                A calendar name used to determine holidays. Defaults to None, which means no holidays are considered.

        Raises:
            ValueError: If an invalid `direction` is provided.

        Returns:
            Date or DateTime:
                The nearest business day for the given reference date.
        """
        if direction not in ("following", "preceding"):
            raise ValueError("Invalid direction. Choose 'following' or 'preceding'.")

        nearest_day = self

        if nearest_day.is_business_day(calendar):
            return nearest_day

        delta = 1 if direction == "following" else -1
        return nearest_day.bizdays_delta(bizdays=delta, calendar=calendar)

    ####################################
    ### DATES DIFF
    ####################################

    @classmethod
    def diff(cls, start_date: Union['Date', 'DateTime', date, datetime], end_date: Union['Date', 'DateTime', date, datetime], periodicity: str = 'D', calendar: str = None) -> int:
        """
        Calculate the difference in periods (days, business days, weeks, months, or years) between two dates.

        This class method calculates the difference in periods (days, business days, weeks, months, or years)
        between two dates. It provides flexibility in choosing the periodicity of the difference calculation.

        Args:
            start_date (Union[Date, DateTime, date, datetime]): The starting date for the difference calculation.
            end_date (Union[Date, DateTime, date, datetime]): The ending date for the difference calculation.
            periodicity (str, optional): The periodicity of the difference calculation. Possible values: 'D', 'B', 'W', 'M', 'Y'. 'D' (default) calculates the difference in days.
            calendar (str, optional): The name of the calendar to use for business day calculations. Defaults to None.

        Raises:
            ValueError: If an invalid `periodicity` value is provided. Valid values are 'D', 'B', 'W', 'M', or 'Y'.

        Returns:
            int: The difference in periods between the two dates, based on the specified periodicity.

        Example:
            To calculate the difference in months between two Date objects:
            >>> start_date = Date(2023, 1, 15)
            >>> end_date = Date(2023, 5, 10)
            >>> Date.diff(start_date, end_date, periodicity='M')
            3

            To calculate the difference in business days between two DateTime objects using a specific calendar:
            >>> start_date = DateTime(2023, 7, 15, 12, 0)
            >>> end_date = DateTime(2023, 7, 20, 12, 0)
            >>> DateTime.diff(start_date, end_date, periodicity='B')
            4
        """
        start_date, end_date = cls.ensure(start_date), cls.ensure(end_date)

        if start_date == end_date:
            return 0

        if periodicity == 'D':
            diff = cls.days_diff(start_date, end_date)
        elif periodicity == 'B':
            diff = cls.bizdays_diff(start_date, end_date, calendar=calendar)
        elif periodicity == 'W':
            diff = cls.weeks_diff(start_date, end_date)
        elif periodicity == 'M':
            diff = cls.months_diff(start_date, end_date)
        elif periodicity == 'Y':
            diff = cls.years_diff(start_date, end_date)
        else:
            raise ValueError("Invalid periodicity. Please choose one of the following: D, B, W, M, Y.")

        return diff

    @classmethod
    def days_diff(cls, start_date: Union[date, datetime, 'Date', 'DateTime'], end_date: Union[date, datetime, 'Date', 'DateTime']) -> int:
        """
        Calculate the difference in days between two dates.

        This class method calculates the difference in days between two dates. It considers the order of the dates and
        returns a positive or negative integer accordingly.

        Args:
            start_date (Union[date, datetime, 'Date', 'DateTime']): The starting date for the difference calculation.
            end_date (Union[date, datetime, 'Date', 'DateTime']): The ending date for the difference calculation.

        Returns:
            int: The difference in days between the two dates. A positive value if end_date is greater than start_date, and a negative value if start_date is greater than end_date.

        Example:
            To calculate the difference in days between two Date objects:
            >>> start_date = Date(2023, 1, 15)
            >>> end_date = Date(2023, 5, 10)
            >>> Date.days_diff(start_date, end_date)
            115

            To calculate the difference in days between two DateTime objects:
            >>> start_date = DateTime(2023, 7, 15, 12, 0)
            >>> end_date = DateTime(2023, 7, 20, 12, 0)
            >>> DateTime.days_diff(start_date, end_date)
            5
        """
        start_date, end_date = cls.ensure(start_date), cls.ensure(end_date)
        start_date, end_date, multiplier = cls._adjust_direction(start_date, end_date)

        days_diff = (end_date - start_date).days

        return days_diff * multiplier

    @classmethod
    def bizdays_diff(cls, start_date: Union[date, datetime, 'Date', 'DateTime'], end_date: Union[date, datetime, 'Date', 'DateTime'], calendar: str = None) -> int:
        """
        Calculate the difference in business days between two dates.

        This class method calculates the difference in business days (weekdays excluding Saturdays and Sundays)
        between two dates. It considers the order of the dates and returns a positive or negative integer accordingly.
        Additionally, it can take into account a custom holiday calendar to exclude holidays from the calculation.

        Args:
            start_date (Union[date, datetime, 'Date', 'DateTime']): The starting date for the difference calculation.
            end_date (Union[date, datetime, 'Date', 'DateTime']): The ending date for the difference calculation.
            calendar (str, optional): The name of the holiday calendar to use for excluding holidays. Defaults to None.

        Returns:
            int: The difference in business days between the two dates. A positive value if end_date is greater than
            start_date, and a negative value if start_date is greater than end_date.

        Example:
            To calculate the difference in business days between two Date objects:
            >>> start_date = Date(2023, 1, 15)
            >>> end_date = Date(2023, 1, 20)
            >>> Date.bizdays_diff(start_date, end_date)
            4

            To calculate the difference in business days between two DateTime objects with a custom holiday calendar:
            >>> start_date = DateTime(2023, 7, 15, 12, 0)
            >>> end_date = DateTime(2023, 7, 20, 12, 0)
            >>> DateTime.bizdays_diff(start_date, end_date)
            4
        """
        start_date, end_date = cls.ensure(start_date), cls.ensure(end_date)
        start_date, end_date, multiplier = cls._adjust_direction(start_date, end_date)

        bdays_diff = 0

        # We need to add one day here to correct calculate the difference
        # https://everysk.atlassian.net/browse/COD-3913
        current = start_date + timedelta(days=1)
        hdays = get_holidays(calendar)

        while current <= end_date:
            if current.weekday() not in (SATURDAY, SUNDAY) and current.date() not in hdays:
                bdays_diff += 1
            current += timedelta(days=1)

        return bdays_diff * multiplier

    @classmethod
    def weeks_diff(cls, start_date: Union[date, datetime, 'Date', 'DateTime'], end_date: Union[date, datetime, 'Date', 'DateTime']) -> int:
        """
        Calculate the difference in weeks between two dates.

        This class method calculates the difference in weeks between two dates. It considers the order of the dates
        and returns a positive or negative integer accordingly.

        Args:
            start_date (Union[date, datetime, 'Date', 'DateTime']): The starting date for the difference calculation.
            end_date (Union[date, datetime, 'Date', 'DateTime']): The ending date for the difference calculation.

        Returns:
            int: The difference in weeks between the two dates. A positive value if end_date is greater than
            start_date, and a negative value if start_date is greater than end_date.

        Example:
            To calculate the difference in weeks between two Date objects:
            >>> start_date = Date(2023, 1, 1)
            >>> end_date = Date(2023, 1, 21)
            >>> Date.weeks_diff(start_date, end_date)
            2

            To calculate the difference in weeks between two DateTime objects:
            >>> start_date = DateTime(2023, 7, 1, 12, 0)
            >>> end_date = DateTime(2023, 7, 15, 12, 0)
            >>> DateTime.weeks_diff(start_date, end_date)
            2
        """
        start_date, end_date = cls.ensure(start_date), cls.ensure(end_date)
        start_date, end_date, multiplier = cls._adjust_direction(start_date, end_date)

        weeks_diff = (end_date - start_date).days // 7

        return weeks_diff * multiplier

    @classmethod
    def months_diff(cls, start_date: Union[date, datetime, 'Date', 'DateTime'], end_date: Union[date, datetime, 'Date', 'DateTime']) -> int:
        """
        Calculate the difference in months between two dates.

        This class method calculates the difference in months between two dates. It considers the order of the dates
        and returns a positive or negative integer accordingly.

        Args:
            start_date (Union[date, datetime, 'Date', 'DateTime']): The starting date for the difference calculation.
            end_date (Union[date, datetime, 'Date', 'DateTime']): The ending date for the difference calculation.

        Returns:
            int: The difference in months between the two dates. A positive value if end_date is greater than start_date, and a negative value if start_date is greater than end_date.

        Example:
            To calculate the difference in months between two Date objects:
            >>> start_date = Date(2023, 1, 1)
            >>> end_date = Date(2023, 3, 15)
            >>> Date.months_diff(start_date, end_date)
            2

            To calculate the difference in months between two DateTime objects:
            >>> start_date = DateTime(2023, 7, 1, 12, 0)
            >>> end_date = DateTime(2024, 3, 15, 12, 0)
            >>> DateTime.months_diff(start_date, end_date)
            8
        """
        start_date, end_date = cls.ensure(start_date), cls.ensure(end_date)
        start_date, end_date, multiplier = cls._adjust_direction(start_date, end_date)

        months_diff = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)

        if end_date.day < start_date.day:
            months_diff -= 1

        return months_diff * multiplier

    @classmethod
    def years_diff(cls, start_date: Union[date, datetime, 'Date', 'DateTime'], end_date: Union[date, datetime, 'Date', 'DateTime']) -> int:
        """
        Calculate the difference in years between two dates.

        This class method calculates the difference in years between two dates. It considers the order of the dates
        and returns a positive or negative integer accordingly.

        Args:
            start_date (Union[date, datetime, 'Date', 'DateTime']): The starting date for the difference calculation.
            end_date (Union[date, datetime, 'Date', 'DateTime']): The ending date for the difference calculation.

        Returns:
            int: The difference in years between the two dates. A positive value if end_date is greater than
            start_date, and a negative value if start_date is greater than end_date.

        Example:
            To calculate the difference in years between two Date objects:
            >>> start_date = Date(2020, 1, 1)
            >>> end_date = Date(2023, 12, 31)
            >>> Date.years_diff(start_date, end_date)
            3

            To calculate the difference in years between two DateTime objects:
            >>> start_date = DateTime(2010, 7, 1, 12, 0)
            >>> end_date = DateTime(2022, 3, 15, 12, 0)
            >>> DateTime.years_diff(start_date, end_date)
            11
        """
        start_date, end_date = cls.ensure(start_date), cls.ensure(end_date)
        start_date, end_date, multiplier = cls._adjust_direction(start_date, end_date)

        years_diff = end_date.year - start_date.year

        if end_date.month < start_date.month or (end_date.month == start_date.month and end_date.day < start_date.day):
            years_diff -= 1

        return years_diff * multiplier

    ####################################
    ### DATES RANGE
    ####################################

    @classmethod
    def range(cls, start_date: Union[date, datetime, 'Date', 'DateTime'], end_date: Union[date, datetime, 'Date', 'DateTime'], periodicity: str = 'D', calendar: str = None) -> list[Self]:
        """
        Generate a range of dates between two dates based on the specified periodicity.

        This class method generates a list of dates between a start date and an end date, based on the specified
        periodicity. The generated list includes both the start and end dates.

        Args:
            start_date (Union[date, datetime, 'Date', 'DateTime']): The starting date of the range.
            end_date (Union[date, datetime, 'Date', 'DateTime']): The ending date of the range.
            periodicity (str, optional): The periodicity of the date range. Options include 'D' (daily) and 'B' (business days). Defaults to 'D'.
            calendar (str, optional): The name of the calendar to use for business day calculations. If None, no holidays are considered. Defaults to None.

        Raises:
            ValueError: If an invalid periodicity is provided or if the date range exceeds 30000 days in length.

        Returns:
            list[Self]: A list of Date or DateTime objects representing the date range.

        Example:
            To generate a daily date range between two Date objects:
            >>> start_date = Date(2023, 1, 1)
            >>> end_date = Date(2023, 1, 5)
            >>> Date.range(start_date, end_date)
            [Date(2023, 1, 1), Date(2023, 1, 2), Date(2023, 1, 3), Date(2023, 1, 4)]

            To generate a business day date range between two DateTime objects:
            >>> start_date = DateTime(2023, 1, 1, 12, 0)
            >>> end_date = DateTime(2023, 1, 7, 12, 0)
            >>> DateTime.range(start_date, end_date, periodicity='B')
            [DateTime(2023, 1, 2, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC')),
             DateTime(2023, 1, 3, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC')),
             DateTime(2023, 1, 4, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC')),
             DateTime(2023, 1, 5, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC')),
             DateTime(2023, 1, 6, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))]
        """
        start_date, end_date = cls.ensure(start_date), cls.ensure(end_date)

        if start_date == end_date:
            return []

        if abs(end_date - start_date).days > date_settings.MAX_DAYS_RANGE:
            raise ValueError('Value out of range')

        dates = None

        if periodicity == 'D':
            dates = cls.days_range(start_date, end_date)
        elif periodicity == 'B':
            dates = cls.bizdays_range(start_date, end_date, calendar=calendar)
        else:
            raise ValueError("Invalid periodicity. Please choose one of the following: D, B.")

        return dates

    @classmethod
    def days_range(cls, start_date: Union[date, datetime, 'Date', 'DateTime'], end_date: Union[date, datetime, 'Date', 'DateTime']) -> list[Self]:
        """
        Generate a daily date range between two dates.

        This class method generates a list of daily dates between a start date (inclusive) and an end date (exclusive).

        Args:
            start_date (Union[date, datetime, 'Date', 'DateTime']): The starting date of the range.
            end_date (Union[date, datetime, 'Date', 'DateTime']): The ending date of the range.

        Returns:
            list[Date or DateTime]: A list of Date or DateTime objects representing the daily date range.

        Example:
            To generate a daily date range between two Date objects:
            >>> start_date = Date(2023, 1, 1)
            >>> end_date = Date(2023, 1, 5)
            >>> Date.days_range(start_date, end_date)
            [Date(2023, 1, 1), Date(2023, 1, 2), Date(2023, 1, 3), Date(2023, 1, 4)]

            To generate a daily date range between two DateTime objects:
            >>> start_date = DateTime(2023, 1, 1, 12, 0)
            >>> end_date = DateTime(2023, 1, 5, 12, 0)
            >>> DateTime.days_range(start_date, end_date)
            [DateTime(2023, 1, 1, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC')),
             DateTime(2023, 1, 2, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC')),
             DateTime(2023, 1, 3, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC')),
             DateTime(2023, 1, 4, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))]
        """
        start_date, end_date = cls.ensure(start_date), cls.ensure(end_date)

        dates = []

        while start_date < end_date:
            dates.append(start_date)
            start_date += timedelta(days=1)

        return dates

    @classmethod
    def bizdays_range(cls, start_date: Union[date, datetime, 'Date', 'DateTime'], end_date: Union[date, datetime, 'Date', 'DateTime'], calendar: str = None) -> list[Self]:
        """
        Generate a business days date range between two dates, excluding weekends and holidays.

        This class method generates a list of business days (weekdays excluding Saturdays, Sundays, and specified holidays)
        between a start date (inclusive) and an end date (exclusive).

        Args:
            start_date (Union[date, datetime, 'Date', 'DateTime']): The starting date of the range.
            end_date (Union[date, datetime, 'Date', 'DateTime']): The ending date of the range.
            calendar (str, optional): A calendar name specifying holidays to be excluded. Defaults to None.

        Returns:
            list[Date or DateTime]: A list of Date or DateTime objects representing the business days date range.

        Example:
            To generate a business days date range between two Date objects, excluding holidays:
            >>> start_date = Date(2023, 1, 1)
            >>> end_date = Date(2023, 1, 5)
            >>> Date.bizdays_range(start_date, end_date)
            [Date(2023, 1, 1), Date(2023, 1, 3), Date(2023, 1, 4)]

            To generate a business days date range between two DateTime objects, excluding holidays:
            >>> start_date = DateTime(2023, 1, 1, 12, 0)s
            >>> end_date = DateTime(2023, 1, 5, 12, 0)
            >>> DateTime.bizdays_range(start_date, end_date)
            [DateTime(2023, 1, 2, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC')),
             DateTime(2023, 1, 3, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC')),
             DateTime(2023, 1, 4, 12, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))]
        """
        start_date, end_date = cls.ensure(start_date), cls.ensure(end_date)

        hdays = get_holidays(calendar)

        dates = []

        while start_date < end_date:
            if start_date.weekday() not in (SATURDAY, SUNDAY) and start_date.date() not in hdays:
                dates.append(start_date)

            start_date += timedelta(days=1)

        return dates
