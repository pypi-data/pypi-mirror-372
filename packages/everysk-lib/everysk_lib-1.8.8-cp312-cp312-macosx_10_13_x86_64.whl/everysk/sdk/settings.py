###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from everysk.core.fields import BoolField, DictField, IntField, StrField

SIMPLE_UNIQUE_ID_LENGTH = IntField(default=8, readonly=True)

EVERYSK_API_SID = StrField()
EVERYSK_API_TOKEN = StrField()

EVERYSK_APP_URL_SCHEME = StrField(default='https')
EVERYSK_APP_URL_DOMAIN = StrField(default='app.everysk.com')
EVERYSK_APP_URL = StrField(default='{EVERYSK_APP_URL_SCHEME}://{EVERYSK_APP_URL_DOMAIN}')

EVERYSK_API_URL_SCHEME = StrField(default='https')
EVERYSK_API_URL_DOMAIN = StrField(default='api.everysk.com')
EVERYSK_API_URL = StrField(default='{EVERYSK_API_URL_SCHEME}://{EVERYSK_API_URL_DOMAIN}')
EVERYSK_SDK_URL = EVERYSK_API_URL

EVERYSK_API_VERSION = StrField(default='v2')
EVERYSK_API_VERIFY_SSL_CERTS = BoolField(default=True)

EVERYSK_SDK_VERSION = StrField(default='v1', readonly=True)
EVERYSK_SDK_ROUTE = StrField(default='sdk_function', readonly=True)

EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT = IntField(default=3600, readonly=True)

EVERYSK_SDK_MODULES_PATH = DictField(default={'WorkerBase': 'everysk.sdk.worker_base.WorkerBase'}, readonly=True)

EVERYSK_SDK_ENTITIES_MODULES_PATH = DictField(
    default={
        'CustomIndex': 'everysk.sdk.entities.custom_index.base.CustomIndex',
        'Datastore': 'everysk.sdk.entities.datastore.base.Datastore',
        'File': 'everysk.sdk.entities.file.base.File',
        'Portfolio': 'everysk.sdk.entities.portfolio.base.Portfolio',
        'PrivateSecurity': 'everysk.sdk.entities.private_security.base.PrivateSecurity',
        'Query': 'everysk.sdk.entities.query.Query',
        'Report': 'everysk.sdk.entities.report.base.Report',
        'Script': 'everysk.sdk.entities.script.Script',
        'Securities': 'everysk.sdk.entities.portfolio.securities.Securities',
        'Security': 'everysk.sdk.entities.portfolio.security.Security',
        'WorkerExecution': 'everysk.sdk.entities.worker_execution.base.WorkerExecution',
        'WorkflowExecution': 'everysk.sdk.entities.workflow_execution.base.WorkflowExecution',
        'Workspace': 'everysk.sdk.entities.workspace.base.Workspace',
    },
    readonly=True,
)

EVERYSK_SDK_ENGINES_MODULES_PATH = DictField(
    default={
        'Expression': 'everysk.sdk.engines.expression.Expression',
        'Compliance': 'everysk.sdk.engines.compliance.Compliance',
        'UserCache': 'everysk.sdk.engines.cache.UserCache',
        'UserLock': 'everysk.sdk.engines.lock.UserLock',
        'MarketData': 'everysk.sdk.engines.market_data.MarketData',
    },
    readonly=True,
)
