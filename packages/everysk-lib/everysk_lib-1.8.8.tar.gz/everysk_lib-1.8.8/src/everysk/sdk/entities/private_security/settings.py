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


PRIVATE_SECURITY_SYMBOL_REGEX = RegexField(default=r'^PRIVATE:[A-Z0-9_]*$', readonly=True)
PRIVATE_SECURITY_SYMBOL_PREFIX = StrField(default='PRIVATE:', readonly=True)

PRIVATE_SECURITY_SYMBOL_MIN_SIZE = IntField(default=9, readonly=True) # len(PRIVATE_SECURITY_SYMBOL_PREFIX) + 1
PRIVATE_SECURITY_SYMBOL_MAX_SIZE = IntField(default=109, readonly=True) # 100 + len(PRIVATE_SECURITY_SYMBOL_PREFIX)
