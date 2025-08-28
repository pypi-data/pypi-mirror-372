###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
# pylint: disable=unused-import

## Remember to prefix all import with EveryskLib to avoid clash with other tests
try:
    from everysk.sdk._tests.base import TestBaseSDK as EveryskLibTestBaseSDK
    from everysk.sdk._tests.init import SDKInitTestCase as EveryskLibSDKInitTestCase
    from everysk.sdk._tests.serialize import (
        SerializeDumpsSDKTestCase as EveryskLibSerializeDumpsSDKTestCase,
        SerializeLoadsSDKTestCase as EveryskLibSerializeLoadsSDKTestCase
    )
    from everysk.sdk._tests.worker_base import WorkerBaseTestCase as EveryskLibWorkerBaseTestCase

    from everysk.sdk.entities._tests.init import InitTestCase as EveryskLibInitTestCase

    from everysk.sdk.engines._tests.cryptography import TestCryptography as EveryskLibTestCryptography
    from everysk.sdk.engines._tests.init import EnginesInitTestCase as EveryskLibEnginesInitTestCase
    from everysk.sdk.engines._tests.compliance import ComplianceTestCase as EveryskLibComplianceTestCase
    from everysk.sdk.engines._tests.cache import CacheTestCase as EveryskLibCacheTestCase
    from everysk.sdk.engines._tests.market_data import (
        MarketDataTestCase as EveryskLibMarketDataTestCase,
        MarketDataPublicTestCase as EveryskLibMarketDataPublicTestCase
    )
    from everysk.sdk.engines._tests.lock import UserLockTestCase as EveryskLibUserLockTestCase
    from everysk.sdk.engines._tests.market_data import MarketDataTestCase as EveryskLibMarketDataTestCase

    from everysk.sdk.entities._tests.base_list import TestEntityList as EveryskLibTestEntityList

    from everysk.sdk.entities._tests.script import ScriptTestCase as EveryskLibScriptTestCase
    from everysk.sdk.entities._tests.base import TestBaseEntity as EveryskLibTestBaseEntity
    from everysk.sdk.entities._tests.tags import TagsTestCase as EveryskLibTestTagsList
    from everysk.sdk.entities._tests.query import QueryTestCase as EveryskLibQueryTestCase

    from everysk.sdk.entities.portfolio._tests.security import TestSecurity as EveryskLibTestSecurity
    from everysk.sdk.entities.portfolio._tests.securities import TestSecurities as EveryskLibTestSecurities
    from everysk.sdk.entities.portfolio._tests.base import (
        TestSecuritiesField as EveryskLibTestTestSecuritiesField,
        TestPortfolio as EveryskLibTestPortfolio
    )

    from everysk.sdk.entities._tests.fields import (
        TestBaseCurrencyField as EveryskLibTestBaseCurrencyField,
        TestEntityTagsField as EveryskLibTestEntityTagsField,
        TestEntityNameField as EveryskLibTestEntityNameField,
        TestEntityDescriptionField as EveryskLibTestEntityDescriptionField,
        TestEntityLinkUIDField as EveryskLibTestEntityLinkUIDField,
        TestEntityWorkspaceField as EveryskLibTestEntityWorkspaceField,
        TestEntityDateTimeField as EveryskLibTestEntityDateTimeField
    )

    from everysk.sdk.entities.custom_index._tests.base import CustomIndexTestCase as EveryskLibCustomIndexTestCase
    from everysk.sdk.entities.datastore.tests.base import DatastoreTestCase as EveryskLibDatastoreTestCase
    from everysk.sdk.entities.private_security._tests.base import PrivateSecurityTestCase as EveryskLibPrivateSecurityTestCase
    from everysk.sdk.entities.file._tests.base import FileTestCase as EveryskLibFileTestCase
    from everysk.sdk.entities.report.tests.base import ReportTestCase as EveryskLibReportTestCase
    from everysk.sdk.entities.worker_execution.tests.base import WorkerExecutionTestCase as EveryskLibWorkerExecutionTestCase
    from everysk.sdk.entities.workflow_execution.tests.base import WorkflowExecutionTestCase as EveryskLibWorkflowExecutionTestCase
    from everysk.sdk.entities.workspace._tests.base import TestWorkspace as EveryskLibTestWorkspace

    from everysk.sdk.engines.helpers.tests.algorithms import (
        NpUniqueTestCase as EveryskLibHelpersNpUniqueTestCase,
        NpSortTestCase as EveryskLibHelpersNpSortTestCase
    )

    from everysk.sdk.engines.expression.tests.base import ExpressionEngineTestCase as EveryskLibExpressionEngineTestCaseNew
    from everysk.sdk.engines.expression.tests.validator import ValidatorTestCase as EveryskLibValidatorTestCaseNew
    from everysk.sdk.engines.expression.tests.interpreter import InterpreterTestCase as EveryskLibInterpreterTestCaseNew

    from everysk.sdk.engines.expression.functions.tests.base import FunctionsBaseTestCase as EveryskLibFunctionsBaseTestCaseNew
    from everysk.sdk.engines.expression.functions.tests.date import FunctionsDateTestCase as EveryskLibFunctionsDateTestCaseNew
    from everysk.sdk.engines.expression.functions.tests.list import FunctionsListTestCase as EveryskLibFunctionsListTestCaseNew
    from everysk.sdk.engines.expression.functions.tests.math import FunctionsMathTestCase as EveryskLibFunctionsMathTestCaseNew
    from everysk.sdk.engines.expression.functions.tests.string import FunctionsStringTestCase as EveryskLibFunctionsStringTestCaseNew
    from everysk.sdk.engines.expression.functions.tests.miscellaneous import FunctionsMiscellaneousTestCase as EveryskLibFunctionsMiscellaneousTestCaseNew
    from everysk.sdk.engines.expression.functions.tests.logic import FunctionsLogicTestCase as EveryskLibFunctionsLogicTestCaseNew

except ModuleNotFoundError as error:
    # This will prevent running these tests if requests is not installed
    if not error.args[0].startswith("No module named 'requests'"):
        raise error
