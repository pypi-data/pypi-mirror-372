###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from everysk.core.fields import StrField, ListField, IntField, RegexField


WORKFLOW_EXECUTION_ID_PREFIX = StrField(default='wfex_', readonly=True)
WORKFLOW_EXECUTION_ID_LENGTH = IntField(default=25, readonly=True)
WORKFLOW_EXECUTION_ID_REGEX = RegexField(default=r'^wfex_[a-zA-Z0-9]{25}', readonly=True)

WORKFLOW_ID_PREFIX = StrField(default='wrkf_', readonly=True)
WORKFLOW_ID_LENGTH = IntField(default=25, readonly=True)
WORKFLOW_ID_REGEX = RegexField(default=r'^wrkf_[a-zA-Z0-9]{25}', readonly=True)

# legacy workflow execution status
WORKFLOW_EXECUTION_STATUS_COMPLETED = StrField(default='COMPLETED', readonly=True)
WORKFLOW_EXECUTION_STATUS_OK = StrField(default='OK', readonly=True)

# current workflow execution status
WORKFLOW_EXECUTION_STATUS_CANCELED = StrField(default='CANCELED', readonly=True)
WORKFLOW_EXECUTION_STATUS_FAILED = StrField(default='FAILED', readonly=True)
WORKFLOW_EXECUTION_STATUS_PREPARING = StrField(default='PREPARING', readonly=True)
WORKFLOW_EXECUTION_STATUS_RUNNING = StrField(default='RUNNING', readonly=True)
WORKFLOW_EXECUTION_STATUS_SUCCEEDED = StrField(default='SUCCEEDED', readonly=True)
WORKFLOW_EXECUTION_STATUS = ListField(default=['CANCELED', 'COMPLETED', 'FAILED', 'OK', 'PREPARING', 'RUNNING', 'SUCCEEDED'], readonly=True)
WORKFLOW_EXECUTION_STATUS_FINISHED = ListField(default=['CANCELED', 'COMPLETED', 'SUCCEEDED', 'FAILED'], readonly=True)
