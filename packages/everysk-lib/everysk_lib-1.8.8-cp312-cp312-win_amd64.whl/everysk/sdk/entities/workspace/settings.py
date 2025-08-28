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
from everysk.core.fields import IntField, RegexField, StrField

###############################################################################
#   Settings Implementation
###############################################################################
ENTITY_WORKSPACE_MAX_LENGTH = IntField(default=50, readonly=True)
ENTITY_WORKSPACE_MIN_LENGTH = IntField(default=1, readonly=True)
ENTITY_WORKSPACE_REGEX = RegexField(default=r'^[a-zA-Z0-9_]*$', readonly=True)

WORKSPACE_GROUP_MAX_LENGTH = IntField(default=50, readonly=True)
WORKSPACE_GROUP_MIN_LENGTH = IntField(default=1, readonly=True)

WORKSPACE_ID_PREFIX = StrField(default='wksp_', readonly=True)
WORKSPACE_DESCRIPTION_MAX_LENGTH = IntField(default=100, readonly=True)
