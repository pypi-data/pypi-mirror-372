###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from everysk.core.fields import IntField, ListField, RegexField, StrField

WORKER_EXECUTION_ID_PREFIX = StrField(default='wkex_', readonly=True)
WORKER_EXECUTION_ID_LENGTH = IntField(default=25, readonly=True)
WORKER_EXECUTION_ID_REGEX = RegexField(default=r'^wkex_[a-zA-Z0-9]{25}', readonly=True)

WORKER_ID_PREFIX = StrField(default='wrkr_', readonly=True)
WORKER_ID_LENGTH = IntField(default=25, readonly=True)
WORKER_ID_REGEX = RegexField(default=r'^wrkr_[a-zA-Z0-9]{25}', readonly=True)

WORKER_EXECUTION_UNFORKED_PARALLEL_INDEX = IntField(default=-1, readonly=True)
WORKER_EXECUTION_UNFORKED_PARALLEL_LENGTH = IntField(default=-1, readonly=True)

WORKER_EXECUTION_STATUS_COMPLETED = StrField(default='COMPLETED', readonly=True)
WORKER_EXECUTION_STATUS_FAILED = StrField(default='FAILED', readonly=True)
WORKER_EXECUTION_STATUS_PREPARING = StrField(default='PREPARING', readonly=True)
WORKER_EXECUTION_STATUS_RUNNING = StrField(default='RUNNING', readonly=True)
WORKER_EXECUTION_STATUS_LIST = ListField(default=['COMPLETED', 'FAILED', 'PREPARING', 'RUNNING'], readonly=True)

WORKER_EXECUTION_INTEGRATION_EVENT_TYPE = StrField(default='INTEGRATION_EVENT', readonly=True)
WORKER_EXECUTION_SCHEDULER_EVENT_TYPE = StrField(default='SCHEDULER_EVENT', readonly=True)
WORKER_EXECUTION_WORKER_FINISHED_EVENT_TYPE = StrField(default='WORKER_FINISHED_EVENT', readonly=True)
WORKER_EXECUTION_MANUAL_EVENT_TYPE = StrField(default='MANUAL', readonly=True)
WORKER_EXECUTION_API_EVENT_TYPE = StrField(default='API', readonly=True)
WORKER_EXECUTION_EVENT_TYPE_LIST = ListField(
    default=['INTEGRATION_EVENT', 'SCHEDULER_EVENT', 'WORKER_FINISHED_EVENT', 'MANUAL', 'API'], readonly=True
)

WORKER_EXECUTION_TYPE_TIME_DRIVEN = StrField(default='TIME_DRIVEN', readonly=True)
WORKER_EXECUTION_TYPE_EVENT_DRIVEN = StrField(default='EVENT_DRIVEN', readonly=True)
WORKER_EXECUTION_TYPE_MANUAL = StrField(default='MANUAL', readonly=True)
WORKER_EXECUTION_TYPE_API = StrField(default='API', readonly=True)
WORKER_EXECUTION_TYPE_LIST = ListField(
    default=['TIME_DRIVEN', 'EVENT_DRIVEN', 'SCHEDULER_EVENT', 'MANUAL', 'API'], readonly=True
)

RESULT_STATUS_OK = StrField(default='OK', readonly=True)
RESULT_STATUS_ERROR = StrField(default='ERROR', readonly=True)

WORKER_TEMPLATE_TYPES = ListField(
    default=[
        'STARTER',
        'BASIC',
        'FORKER',
        'BARRIER',
        'CONDITIONAL',
        'TRY',
        'CATCH',
        'ENDER',
        'Retrieve',
    ],  # Retrieve is a legacy type.
    readonly=True,
)
