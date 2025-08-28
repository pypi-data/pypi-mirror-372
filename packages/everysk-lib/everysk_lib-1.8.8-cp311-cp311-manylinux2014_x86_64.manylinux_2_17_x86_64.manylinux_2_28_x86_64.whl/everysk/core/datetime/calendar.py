###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from functools import cache

import holidays
from holidays.countries import BR

from everysk.core.datetime import Date


class BRHolidays(BR):
    """
    Subclass of BR representing holidays specific to Brazil and also provides further functionality
    """

    def _populate(self, year: int) -> None:
        """
        Populate holidays specific to Brazil for the given year.

        Args:
            year (int): The year for which holidays are to be populated.

        Example:
            >>> from everysk.core.datetime.calendar import BRHolidays
            >>> br_holidays = BRHolidays()
            >>> br_holidays._populate(2022)
            >>> print(br_holidays)
            {
                datetime.date(2022, 1, 1): 'Confraternização Universal',
                datetime.date(2022, 4, 15): 'Sexta-feira Santa',
                ...
            }
        """
        super()._populate(year)

        # We need to check individually for these holidays
        try:
            self.pop_named('Início da Quaresma')
        except KeyError:
            pass

        try:
            self.pop_named('Dia do Servidor Público')
        except KeyError:
            pass

        try:
            self.pop_named('Véspera de Natal')
        except KeyError:
            pass

        try:
            self.pop_named('Véspera de Ano-Novo')
        except KeyError:
            pass


class ANBIMA(BRHolidays):
    pass


class BVMF(BRHolidays):
    """
    Subclass of BRHolidays representing holidays specific to the BVMF calendar.
    """
    def _populate(self, year: int) -> None:
        """
        _summary_

        Args:
            year (int): The year for the holidays to be populated

        Example:
            Display the holidays for the year of 2022

            >>> from everysk.core.datetime.calendar import BVMF
            >>> bvmf_holidays = BVMF()
            >>> bvmf_holidays._populate(2022)
            >>> print(bvmf_holidays)
            {
                datetime.date(2022, 1, 1): 'Confraternização Universal',
                datetime.date(2022, 4, 15): 'Sexta-feira Santa',
                ...
            }
        """
        super()._populate(year)

        if year < 2022:
            self[Date(year, 1, 25)] = 'Aniversário de São Paulo'
            self[Date(year, 11, 20)] = 'Dia da Consciência Negra'


def get_holidays(calendar: str, years: list = range(2000, 2100)) -> dict:
    """
    Uses the holidays library (https://pypi.org/project/holidays/) to retrieve a list of holidays for a specific country

    It also uses a range of years, if more specification needed

    Args:
        calendar (str): Two digit country symbol.
        years (list, optional): List of int years. Ex: [2021, 2022]. Defaults to [2000, ..., 2099].

    Example:
        Getting holidays for Brazil (BVMF calendar) for the years 2021 and 2022.

        >>> from everysk.core.datetime.calendar import get_holidays
        >>> brazil_holidays = get_holidays('BR', years=[2021, 2022])
        >>> print(brazil_holidays)
        {
            datetime.date(2021, 1, 1) : 'Confraternização Universal',
            datetime.date(2021, 4, 2) : 'Sexta-feira Santa',
            ...
        }
    """
    return _get_holidays(calendar=calendar, years=tuple(years))


@cache
def _get_holidays(calendar: str, years: tuple[int]) -> dict:
    """
    Cacheable version of get_holidays.
    """
    holidays.BVMF = BVMF
    holidays.ANBIMA = ANBIMA
    holidays.BRHolidays = BRHolidays

    # We need to remove some holidays for the BR calendar so we change it
    if calendar == 'BR':
        calendar = 'BRHolidays'

    # Every country has public holidays
    # Brazil has optional holidays as well
    categories = ['public']
    if calendar in {'BRHolidays', 'BVMF', 'ANBIMA'}:
        categories.append('optional')

    return {Date(dt.year, dt.month, dt.day): name for dt, name in holidays.country_holidays(calendar, years=years, categories=categories).items()}
