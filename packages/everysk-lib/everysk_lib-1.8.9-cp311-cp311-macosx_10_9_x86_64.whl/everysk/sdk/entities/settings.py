###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################

###############################################################################
#   Imports
###############################################################################
from everysk.core.fields import IntField, StrField, SetField, ListField

###############################################################################
#   Settings Implementation
###############################################################################
ENTITY_NAME_MAX_LENGTH = IntField(default=200, readonly=True)
ENTITY_NAME_MIN_LENGTH = IntField(default=1, readonly=True)

ENTITY_DESCRIPTION_MAX_LEN = IntField(default=500, readonly=True)
ENTITY_DESCRIPTION_MIN_LEN = IntField(default=0, readonly=True)

ENTITY_MAX_TAG_LENGTH = IntField(default=252, readonly=True)
ENTITY_MIN_TAG_LENGTH = IntField(default=1, readonly=True)
ENTITY_MAX_TAG_SIZE = IntField(default=32, readonly=True)
ENTITY_MIN_TAG_SIZE = IntField(default=0, readonly=True)

ENTITY_DEFAULT_VERSION = StrField(default='v1', readonly=True)
ENTITY_ID_LENGTH = IntField(default=25, readonly=True)

ENTITY_MAX_TAG_SIZE = IntField(default=32, readonly=True)
ENTITY_MIN_TAG_SIZE = IntField(default=0, readonly=True)

ENTITY_LINK_UID_MAX_LENGTH = IntField(default=128, readonly=True)
ENTITY_LINK_UID_MIN_LENGTH = IntField(default=1, readonly=True)

DEFAULT_QUERY_OFFSET = IntField(default=0, readonly=True)
DEFAULT_QUERY_PAGE_SIZE = IntField(default=20, readonly=True)
DEFAULT_QUERY_LIMIT = IntField(default=None)

ENTITY_RETRIEVE_BATCH_SIZE = IntField(default=1000, readonly=True)

QUERY_OPERATORS = SetField(default={'<=', '>=', '<', '>', '=', '!=', 'IN', 'NOT_IN'}, readonly=True)

ENTITY_BASE_CURRENCY_DEFAULT_LIST = SetField(default={'USD', 'EUR', 'GBP', 'JPY', 'CNY', 'AUD', 'CAD', 'CHF', 'CNH', 'HKD', 'NZD', 'BRL'}, readonly=True)
ENTITY_ALLOWED_QUERY_ATTRIBUTES_FOR_ALL_OPERATORS = ListField(default=['name', 'date', 'link_uid', 'created_on', 'updated_on'], readonly=True)
