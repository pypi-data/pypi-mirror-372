###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from everysk.core.fields import StrField, IntField, RegexField


DATASTORE_ID_REGEX = RegexField(default=r'^dats_[a-zA-Z0-9]', readonly=True)
DATASTORE_ID_PREFIX = StrField(default='dats_', readonly=True)
DATASTORE_ID_MAX_SIZE = IntField(default=30, readonly=True)

DATASTORE_LEVEL_MAX_LENGTH = IntField(default=32, readonly=True)
