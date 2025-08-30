###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from calendar import monthrange

from typing import Self

from everysk.core.datetime import date_settings
from everysk.core.exceptions import DateError


class DateExpressionMixin:

    @classmethod
    def get_date_from_expression(cls, expression: str, year: int, month: int, day: str = None, calendar: str = None) -> Self: # pylint: disable=too-many-return-statements
        """
        This function takes an expression, year, and a month, then
        it returns a Date object containing the year, month, and day that correspond to
        the `expression` passed as input.

        Args:
            expression (str): The expression that contains an element that will be used to extract the date.
            year (int): The desired year for the date
            month (int): The desired month for the date.
            calendar (str, optional): The Calendar that will be used to extract the holidays. Defaults to None.

        Returns:
            Date: The Date object containing the date based on the expression elements.

        Example:
            Get the 15th day of January in the year 2024
            >>> Date.get_date_from_expression('15th day', 2024, 1)
            Date(2024, 1, 15)

            Get the 15th business day of January in the year 2024
            >>> Date.get_date_from_expression('15th bizday', 2024, 1, calendar='ANBIMA')
            Date(2024, 1, 29)

            Get the date of the previous business day
            >>> Date.get_date_from_expression('previous bizday', 2024, 8, 16, calendar='ANBIMA')
            Date(2024, 8, 15)

            Get the date of the next business day
            >>> Date.get_date_from_expression('next bizday', 2024, 8, 16, calendar='ANBIMA')
            Date(2024, 8, 19)

            Get first Wednesday which is a Business day after a specific day
            >>> Date.get_date_from_expression('first wed bizday after 15th day', 2024, 11, calendar='ANBIMA')
            Date(2024, 11, 27)

            Get first Wednesday which is a Business day before a specific day
            >>> Date.get_date_from_expression('first wed bizday before 15th day', 2024, 11, calendar='ANBIMA')
            >>> Date(2024, 11, 13)
        """
        token = expression.lower().split()

        if len(token) == 2:
            num = cls._convert_ordinal_to_number(token[0])

            if token[0] in ('previous', 'next') and token[1] == 'bizday':
                return cls._calculate_positional_business_day(token[0], year, month, day, calendar)

            if token[1] == 'day':
                return cls._calculate_ordinal_day(num, year, month)

            if token[1] == 'bizday':
                return cls._calculate_ordinal_business_day(num, year, month, calendar)

            raise ValueError(f'Invalid day: {token[1]}')

        if len(token) == 5:
            if token[0] not in ('first', 'second', 'third'):
                raise ValueError(f'Invalid Written Ordinal: {token[0]}')

            day_number = cls._convert_ordinal_to_number(token[3])
            day_position = cls._convert_ordinal_to_number(token[0])

            if token[2] == 'after':
                return cls._calculate_bizday_relative_to_specific_date(day_number, day_position, year, month, calendar)

            if token[2] == 'before':
                return cls._calculate_bizday_relative_to_specific_date(day_number, -day_position, year, month, calendar)

            raise ValueError(f'Invalid expression: {token[2]}, the day reference must be either "before" or "after"')

        if len(token) == 6:
            if token[0] not in ('first', 'second', 'third'):
                raise ValueError(f'Invalid Written Ordinal: {token[0]}, it must be either "first", "second", or "third"')

            day_position = cls._convert_ordinal_to_number(token[0])

            day_number = cls._convert_ordinal_to_number(token[4])

            if token[1] in date_settings.WEEKDAYS and token[2] == 'bizday' and token[3] in ('after', 'before'):
                return cls._calculate_bizday_relative_to_specific_date_and_week_day(token[1], day_position, day_number, year, month, token[3], calendar)

            raise ValueError('Invalid expression, please verify the day type or the week days')

        raise ValueError(f'Invalid expression: {expression}, please refer to the documentation.')

    @classmethod
    def _convert_ordinal_to_number(cls, nth: str) -> int:
        """
        This method takes a string that represents a date in ordinal format
        and returns an integer accordingly.

        Args:
            nth (str): The expression that includes date number

        Returns:
            int: The integer that represents the date in the previous format string.

        Example:
            >>> _convert_ordinal_to_number("first")
            1

            >>> _convert_ordinal_to_number("second")
            2

            >>> _convert_ordinal_to_number("18th day")
            18

            >>> _convert_ordinal_to_number("22th day")
            22
        """
        if nth == 'first':
            return 1

        if nth == 'second':
            return 2

        if nth == 'third':
            return 3

        if nth == 'last':
            return -1

        if nth[-2:] in ('th', 'st', 'nd', 'rd'):
            return int(nth[:-2])

        if nth in ('previous', 'next'):
            return 1

        raise ValueError(f'Invalid nth: {nth}')

    @classmethod
    def _calculate_positional_business_day(cls, position: str, year: int, month: int, day: int, calendar: str = None) -> Self:
        """
        This private method takes a position, that will be either "previous" or "next", and returns
        the a business day based on the `position` argument.

        Args:
            position (str): The position that will be taken into account for the Date calculation. This will be either "previous" or "next".
            year (int): The year desired.
            month (int): The month desired.
            day (int): The day which will be used for reference for the position.
            calendar (str, optional): The type of calendar that will be used for business days or holidays. Defaults to None.

        Returns:
            Date: The Date object containing the date based on the position
        """
        if position == 'previous':
            return cls(year, month, day).bizdays_delta(-1, calendar) # pylint: disable=no-member

        return cls(year, month, day).bizdays_delta(1, calendar) # pylint: disable=no-member

    @classmethod
    def _calculate_ordinal_day(cls, num: int, year: int, month: int) -> Self:
        """
        This private method takes a day number, year, and month then it simply converts
        to a Date object.

        Args:
            num (int): The day number.
            year (int): The year desired.
            month (int, optional): The month number.

        Returns:
            Date: The Date object with `year`, `month`, and `num` respectively.
        """
        if num == -1:
            num = monthrange(year, month)[1]

        return cls(year, month, num)

    @classmethod
    def _calculate_ordinal_business_day(cls, num: int, year: int, month: int, calendar: str = None) -> Self:
        """
        This private method takes a day number, month, and year then returns a Date object containing
        the date corresponding to the `num` nth business day of that year and month.

        Args:
            num (int): The ordinal date converted to integer.
            year (int): The year to perform the calculation.
            month (int): The month number for the calculation.
            calendar (str, optional): The calendar that will be used with the dates.

        Returns:
            Date: The Date object with the corresponding date accounted for bizdays.
        """
        start_date = cls(year, month, 1).get_first_day_of_month(True, calendar)
        end_date = cls(year, month, 1).get_last_day_of_month(True, calendar)
        list_of_bizdays_for_the_month = cls.bizdays_range(start_date, end_date.bizdays_delta(1), calendar)

        try:
            if num == -1:
                return list_of_bizdays_for_the_month[num]

            return list_of_bizdays_for_the_month[num - 1]

        except IndexError as error:
            raise DateError(f'Invalid Business Day, the current month only has {cls._calculate_number_of_bizdays_for_the_month(year, month, calendar)}, your value was {num}') from error

    @classmethod
    def _calculate_bizday_relative_to_specific_date(cls, day_number: int, ordinal_position: str, year: int, month: int, calendar: str = None) -> Self:
        """
        This private method is used to perform the calculation for retrieving a Date
        before or after a specific date using a set of inputs.

        Args:
            day_number (int): The integer that corresponds to the day of the month.
            ordinal_position (str): The ordinal format of one, two, and three.
            year (int): The year for the calculation.
            month (int): The month for the calculation.
            calendar (str, optional):  The calendar that will be used for extracting business days or holidays. Defaults to None.

        Returns:
            Date: The Date object that will contain the business day before or after a specific date.
        """
        current_date = cls(year, month, day_number)
        current_date = current_date.bizdays_delta(ordinal_position, calendar) # pylint: disable=no-member

        return current_date

    @classmethod
    def _calculate_bizday_relative_to_specific_date_and_week_day(cls, day_of_week: str, day_position: str, day_number: int, year: int, month: int, date_reference: str, calendar: str = None) -> Self:
        """
        This private method is used in order to calculate a specific business day thats either before or
        after a date and week day.

        Args:
            day_of_week (str): The day name.
            day_position (str): The position of the date, it can be first, second, or third.
            day_number (int): The day of the month.
            year (int): The year for the calculation.
            month (int): The month for the calculation.
            calendar (str, optional): The type of calendar that will be usd for the business days and holidays. Defaults to None.

        Raises:
            ValueError: If the date reference is invalid, it will raise an error

        Returns:
            Date: The Date object containing the date calculated.
        """
        current_date = cls(year, month, day_number)
        bizdays_for_the_day_name = []

        if date_reference == 'before':
            start_date = cls(year, month, day_number).months_delta(-1).get_first_day_of_month(True, calendar) # pylint: disable=no-member
            list_of_bizdays = cls.bizdays_range(start_date, current_date, calendar) # pylint: disable=no-member

        elif date_reference == 'after':
            end_date = cls(year, month, day_number).months_delta(1).get_last_day_of_month(True, calendar) # pylint: disable=no-member
            list_of_bizdays = cls.bizdays_range(current_date, end_date, calendar) # pylint: disable=no-member

        else:
            raise ValueError(f'Invalid date reference: {date_reference}')

        for days in list_of_bizdays:
            if day_of_week in days.day_name.lower():
                bizdays_for_the_day_name.append(days)

        return bizdays_for_the_day_name[-day_position if date_reference == 'before' else day_position -1]

    @classmethod
    def _calculate_number_of_bizdays_for_the_month(cls, year: int, month: int, calendar: str = None) -> int:
        """
        This method takes a year, a month, and optionally a calendar, then returns an
        integer indicating the number of business days for the month.

        Args:
            year (int): The year for the calculation.
            month (int): The month for the calculation
            calendar (str, optional): The type of calendar to extract the business days or holidays. Defaults to None.

        Returns:
            int: The number of business days for the month
        """
        start_date = cls(year, month, 1).get_first_day_of_month(True, calendar) # pylint: disable=no-member
        end_date = cls(year, month, 1).get_last_day_of_month(True, calendar) # pylint: disable=no-member
        list_of_bizdays = cls.bizdays_range(start_date, end_date.bizdays_delta(1), calendar) # pylint: disable=no-member

        return len(list_of_bizdays)
