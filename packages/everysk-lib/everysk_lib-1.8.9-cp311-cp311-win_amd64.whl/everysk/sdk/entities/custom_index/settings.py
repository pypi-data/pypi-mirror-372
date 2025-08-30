###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from everysk.core.fields import StrField, IntField, FloatField, RegexField


CUSTOM_INDEX_SYMBOL_REGEX = RegexField(default=r'^CUSTOM:[A-Z0-9_]*$', readonly=True)
CUSTOM_INDEX_SYMBOL_PREFIX = StrField(default='CUSTOM:', readonly=True)

CUSTOM_INDEX_SYMBOL_MIN_SIZE = IntField(default=8, readonly=True) # len(CUSTOM_INDEX_SYMBOL_PREFIX) + 1
CUSTOM_INDEX_SYMBOL_MAX_SIZE = IntField(default=107, readonly=True) # len(CUSTOM_INDEX_SYMBOL_PREFIX) + 100

CUSTOM_INDEX_MIN_DATA_BLOB = IntField(default=1, readonly=True)

CUSTOM_INDEX_BASE_PRICE_MIN_VAL = FloatField(default=-9999999999999.99, readonly=True)
CUSTOM_INDEX_BASE_PRICE_MAX_VAL = FloatField(default=+9999999999999.99, readonly=True)

CUSTOM_INDEX_DATA_TYPE_PRICE = StrField(default='PRICE', readonly=True)
CUSTOM_INDEX_DATA_TYPE_RETURN = StrField(default='RETURN', readonly=True)
CUSTOM_INDEX_DATA_TYPE_RETURN_100 = StrField(default='RETURN_100', readonly=True)

CUSTOM_INDEX_PERIODICITY_MONTHLY = StrField(default='M', readonly=True)
CUSTOM_INDEX_PERIODICITY_DAILY = StrField(default='D', readonly=True)
