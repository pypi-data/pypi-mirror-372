###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from everysk.core.fields import FloatField, IntField, ListField, StrField, TupleField

ENGINES_EXPRESSION_DEFAULT_DATA_TYPES = TupleField(default=('cpp_var', 'str_var'), readonly=True)
ENGINES_CACHE_EXECUTION_EXPIRATION_TIME = IntField(default=14400, readonly=True)
ENGINES_MARKET_DATA_TICKER_TYPES = ListField(default=('everysk_symbol', 'everysk_id', None), readonly=True)

MARKET_DATA_PUBLIC_URL = StrField(default='https://public-market-data-1088321674060.us-central1.run.app', readonly=True)
USER_CACHE_LOCK_EXPIRATION_TIME = FloatField(default=10.0, readonly=True)
USER_CACHE_LOCK_MIN_EXPIRATION_TIME = FloatField(default=0.01, readonly=True)
USER_CACHE_LOCK_MAX_EXPIRATION_TIME = FloatField(default=60.0, readonly=True)
