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


REPORT_ID_REGEX = RegexField(default=r'^repo_[a-zA-Z0-9]', readonly=True)
REPORT_ID_PREFIX = StrField(default='repo_', readonly=True)

REPORT_ID_MAX_SIZE = IntField(default=30, readonly=True)
REPORT_LEVEL_MAX_LENGTH = IntField(default=32, readonly=True)

REPORT_AUTHORIZATION_PUBLIC = StrField(default='public', readonly=True)
REPORT_AUTHORIZATION_PRIVATE = StrField(default='private', readonly=True)
REPORT_AUTHORIZATION_REGEX = RegexField(default=r'public|private', readonly=True)

REPORT_URL_PATH = StrField(default='/report', readonly=True)
