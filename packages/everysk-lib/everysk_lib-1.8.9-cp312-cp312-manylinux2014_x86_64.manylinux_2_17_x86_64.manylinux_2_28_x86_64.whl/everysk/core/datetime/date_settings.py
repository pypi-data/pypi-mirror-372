###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from datetime import datetime, date
from zoneinfo import ZoneInfo


# pylint: disable=not-callable
MARKET_START_DATE_TIME: datetime = datetime(2008, 1, 1, tzinfo=ZoneInfo('UTC'))
MARKET_START_DATE: date = date(2008, 1, 1)

DEFAULT_TIME_ZONE: str = 'UTC'

DEFAULT_DATE_FORMAT: str = '%Y%m%d'
DEFAULT_DATE_TIME_FORMAT: str = '%Y%m%d %H:%M:%S'
DEFAULT_TIME_FORMAT: str = '%H:%M:%S'
DEFAULT_FORCE_TIME: str = 'MIDDAY'

DEFAULT_DATE_FORMAT_LEN: str = 8
DEFAULT_DATE_TIME_FORMAT_LEN: str = 17

MAX_DAYS_RANGE: int = 30000

WEEKDAYS = ('mon', 'tue', 'wed', 'thu', 'fri')
