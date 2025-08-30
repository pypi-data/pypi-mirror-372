###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from everysk.core.fields import FloatField, IntField, ListField, RegexField, StrField

PORTFOLIO_ID_REGEX = RegexField(default=r'^port_[a-zA-Z0-9]', readonly=True)
PORTFOLIO_ID_PREFIX = StrField(default='port_', readonly=True)
PORTFOLIO_ID_MAX_SIZE = IntField(default=30, readonly=True)  # len(PORTFOLIO_ID_PREFIX) + ENTITY_ID_LENGTH

PORTFOLIO_MAX_SIZE = IntField(default=40000, readonly=True)
PORTFOLIO_LEVEL_MAX_LENGTH = IntField(default=32, readonly=True)

SECURITY_STATUS_OK = StrField(default='OK', readonly=True)
SECURITY_STATUS_ERROR = StrField(default='ERROR', readonly=True)
SECURITY_STATUS_DELISTED = StrField(default='DELISTED', readonly=True)
SECURITY_ID_LENGTH = IntField(default=6, readonly=True)
SECURITY_ID_PREFIX = StrField(default='sec_', readonly=True)
SYMBOL_ID_MAX_LEN = IntField(default=100, readonly=True)

PRICE_MIN_VALUE = FloatField(default=-9999999999999.99, readonly=True)
PRICE_MAX_VALUE = FloatField(default=+9999999999999.99, readonly=True)

FX_RATE_MIN_VALUE = FloatField(default=0.0, readonly=True)
FX_RATE_MAX_VALUE = FloatField(default=+9999999999999.99, readonly=True)

MULTIPLIER_MIN_VALUE = FloatField(default=0.0, readonly=True)
MULTIPLIER_MAX_VALUE = FloatField(default=+9999999999999.99, readonly=True)

QUANTITY_MIN_VALUE = FloatField(default=-9999999999999.99, readonly=True)
QUANTITY_MAX_VALUE = FloatField(default=+9999999999999.99, readonly=True)

SYMBOL_MAX_LENGTH = IntField(default=100, readonly=True)
LABEL_MAX_LENGTH = IntField(default=100, readonly=True)

PORTFOLIO_SECURITY_ERROR_TYPE_MAX_LEN = IntField(default=100, readonly=True)
PORTFOLIO_SECURITY_ERROR_MESSAGE_MAX_LEN = IntField(default=500, readonly=True)
PORTFOLIO_SECURITY_TYPE_MAX_LEN = IntField(default=100, readonly=True)

PORTFOLIO_PROPERTIES_ORDER = ListField(
    default=[
        'status',
        'id',
        'symbol',
        'quantity',
        'instrument_class',
        'ticker',
        'label',
        'name',
        'isin',
        'exchange',
        'currency',
        'fx_rate',
        'market_price',
        'market_value',
        'instrument_type',
        'instrument_subtype',
        'asset_class',
        'asset_subclass',
        'error_type',
        'error_message',
        'maturity_date',
        'indexer',
        'percent_index',
        'rate',
        'coupon',
        'multiplier',
        'underlying',
        'series',
        'option_type',
        'strike',
        'issue_price',
        'issue_date',
        'issuer',
        'issuer_type',
        'cost_price',
        'unrealized_pl',
        'unrealized_pl_in_base',
        'book',
        'trader',
        'trade_id',
        'operation',
        'accounting',
        'warranty',
        'return_date',
        'settlement',
        'look_through_reference',
        'extra_data',
        'hash',
    ],
    readonly=True,
)
