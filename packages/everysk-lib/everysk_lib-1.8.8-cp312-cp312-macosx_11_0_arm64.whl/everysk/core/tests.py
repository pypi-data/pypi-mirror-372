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

## Cloud function Test Cases
try:
    from everysk.core.cloud_function.tests import CloudFunctionTestCase as EveryskLibCloudFunctionTestCase
except ModuleNotFoundError as error:
    # This will prevent running these tests if redis is not installed
    if not error.args[0].startswith("No module named 'redis'"):
        raise error

## Compress Test Cases
from everysk.core._tests.compress import (
    CompressTestCase as EveryskLibCompressTestCase,
    CompressGzipJsonTestCase as EveryskLibCompressGzipJsonTestCase,
    CompressGzipPickleTestCase as EveryskLibCompressGzipPickleTestCase,
    CompressZlibJsonTestCase as EveryskLibCompressZlibJsonTestCase,
    CompressZlibPickleTestCase as EveryskLibCompressZlibPickleTestCase,
    FileHandlingTestCase as EveryskLibFileHandlingTestCase
)

## Config Test Cases
from everysk.core._tests.config import (
    SettingsModulesTestCase as EveryskLibSettingsModulesTestCase,
    SettingsTestCase as EveryskLibSettingsTestCase,
    SettingsManagerTestCase as EveryskLibSettingsManagerTestCase
)

## Date, DateTime Test Cases
from everysk.core.datetime.tests.date import DateTestCase as EveryskLibDateTestCase
from everysk.core.datetime.tests.datetime import DateTimeTestCase as EveryskLibDateTimeTestCase
from everysk.core.datetime.tests.date_mixin import GetHolidaysTestCase as EveryskLibDateMixinGetHolidaysTestCase
from everysk.core.datetime.tests.calendar import CalendarTestCase as EveryskLibCalendarTestCase

## Exceptions Test Cases
from everysk.core._tests.exceptions import (
    BaseExceptionTestCase as EveryskLibBaseExceptionTestCase,
    DefaultErrorTestCase as EveryskLibDefaultErrorTestCase,
    HttpErrorTestCase as EveryskLibHttpErrorTestCase,
    FieldValueErrorTestCase as EveryskLibFieldValueErrorTestCase,
    ReadonlyErrorTestCase as EveryskLibReadonlyErrorTestCase,
    RequiredErrorTestCase as EveryskLibRequiredErrorTestCase,
    TestAPIError as EveryskLibTestAPIError,
    HandledExceptionTestCase as EveryskLibHandledExceptionTestCase,
    SDKExceptionsTestCase as EveryskLibSDKExceptionsTestCase
)

## Fields Test Cases
from everysk.core._tests.fields import (
    BoolFieldTestCase as EveryskLibBoolFieldTestCase,
    ChoiceFieldTestCase as EveryskLibChoiceFieldTestCase,
    DateFieldTestCase as EveryskLibDateFieldTestCase,
    DateTimeFieldTestCase as EveryskLibDateTimeFieldTestCase,
    DictFieldTestCase as EveryskLibDictFieldTestCase,
    FieldTestCase as EveryskLibFieldTestCase,
    FieldUndefinedTestCase as EveryskLibFieldUndefinedTestCase,
    FloatFieldTestCase as EveryskLibFloatFieldTestCase,
    IntFieldTestCase as EveryskLibIntFieldTestCase,
    IteratorFieldTestCase as EveryskLibIteratorFieldTestCase,
    ListFieldTestCase as EveryskLibListFieldTestCase,
    StrFieldTestCase as EveryskLibStrFieldTestCase,
    TupleFieldTestCase as EveryskLibTupleFieldTestCase,
    ObjectInitPropertyTestCase as EveryskLibObjectInitPropertyTestCase,
    COD3770TestCase as EveryskLibCOD3770TestCase,
    URLFieldTestCase as EveryskLibURLFieldTestCase,
    SetFieldTestCase as EveryskLibSetFieldTestCase,
    EmailFieldTestCase as EveryskLibEmailFieldTestCase
)

## Firestore Test Cases
try:
    from everysk.core._tests.firestore import (
        BaseDocumentCachedConfigTestCase as EveryskLibBaseDocumentCachedConfigTestCase,
        BaseDocumentConfigTestCase as EveryskLibBaseDocumentConfigTestCase,
        DocumentCachedTestCase as EveryskLibDocumentCachedTestCase,
        DocumentTestCase as EveryskLibDocumentTestCase,
        FirestoreClientTestCase as EveryskLibFirestoreClientTestCase,
        LoadsPaginatedTestCase as EveryskLibLoadsPaginatedTestCase
    )
except ModuleNotFoundError as error:
    # This will prevent running these tests if google-cloud-firestore is not installed
    if not error.args[0].startswith("No module named 'google"):
        raise error

## Http Test Cases
try:
    from everysk.core._tests.http import (
        HttpConnectionTestCase as EveryskLibHttpConnectionTestCase,
        HttpConnectionConfigTestCase as EveryskLibHttpConnectionConfigTestCase,
        HttpGETConnectionTestCase as EveryskLibHttpGETConnectionTestCase,
        HttpPOSTConnectionTestCase as EveryskLibHttpPOSTConnectionTestCase,
        HttpSDKPOSTConnectionTestCase as EveryskLibHttpSDKPOSTConnectionTestCase,
        HttpPOSTCompressedConnectionTestCase as EveryskLibHttpPOSTCompressedConnectionTestCase,
        HttpDELETEConnectionTestCase as EveryskLibHttpDELETEConnectioNTestCase,
        HttpHEADConnectionTestCase as EveryskLibHttpHEADConnectionTestCase,
        HttpOPTIONSConnectionTestCase as EveryskLibHttpOPTIONSConnectionTestCase,
        HttpPATCHConnectionTestCase as EveryskLibHttpPATCHConnectionTestCase,
        HttpPUTConnectionTestCase as EveryskLibHttpPUTCompressedConnectionTestCase
    )
except ModuleNotFoundError as error:
    # This will prevent running these tests if requests is not installed
    if not error.args[0].startswith("No module named 'requests'"):
        raise error

## Log Test Cases
from everysk.core._tests.log import (
    LoggerExtraDataTestCase as EveryskLibLoggerExtraDataTestCase,
    LoggerFormatterTestCase as EveryskLibLoggerFormatterTestCase,
    LoggerManagerTestCase as EveryskLibLoggerManagerTestCase,
    LoggerMethodsTestCase as EveryskLibLoggerMethodsTestCase,
    LoggerTestCase as EveryskLibLoggerTestCase,
    LoggerTraceTestCase as EveryskLibLogTraceTestCase,
    LoggerStdoutTestCase as EveryskLibLoggerStdoutTestCase,
    LoggerJsonTestCase as EveryskLibLoggerJsonTestCase,
)
try:
    from everysk.core._tests.log import LoggerSlackTestCase as EveryskLibLoggerSlackTestCase # We need requests to run this test
except ModuleNotFoundError as error:
    # This will prevent running these tests if requests is not installed
    if not error.args[0].startswith("No module named 'requests'"):
        raise error


## Object Test Cases
from everysk.core._tests.object import (
    BaseDictPropertyTestCase as EveryskLibBaseDictPropertyTestCase,
    BaseDictTestCase as EveryskLibBaseDictTestCase,
    BaseFieldTestCase as EveryskLibBaseFieldTestCase,
    BaseObjectTestCase as EveryskLibBaseObjectTestCase,
    ConfigHashTestCase as EveryskLibConfigHashTestCase,
    FrozenDictTestCase as EveryskLibFrozenDictTestCase,
    FrozenObjectTestCase as EveryskLibFrozenObjectTestCase,
    MetaClassConfigTestCase as EveryskLibMetaClassConfigTestCase,
    RequiredTestCase as EveryskLibRequiredTestCase,
    ValidateTestCase as EveryskLibValidateTestCase,
    MetaClassAttributesTestCase as EveryskLibMetaClassAttributesTestCase,
    NpArrayTestCase as EveryskLibNpArrayTestCase,
    AfterInitTestCase as EveryskLibAfterInitTestCase,
    BeforeInitTestCase as EveryskLibBeforeInitTestCase,
    SilentTestCase as EveryskLibSilentTestCase,
    TypingCheckingTestCase as EveryskLibTypingCheckingTestCase,
    BaseDictSuperTestCase as EveryskLibBaseDictSuperTestCase
)

## Number Test Cases
from everysk.core._tests.number import NumberTestCase as EveryskLibNumberTestCase

## Signing Test Cases
from everysk.core._tests.signing import (
    SignTestCase as EveryskLibSignTestCase,
    UnsignTestCase as EveryskLibUnsignTestCase
)

## String Test Cases
from everysk.core._tests.string import StringTestCase as EveryskLibStringTestCase

## Redis Test Cases
try:
    from everysk.core._tests.redis import (
        RedisCacheCompressedTestCase as EveryskLibRedisCacheCompressedTestCase,
        RedisCacheTestCase as EveryskLibRedisCacheTestCase,
        RedisChannelTestCase as EveryskLibRedisChannelTestCase,
        RedisClientTestCase as EveryskLibRedisClientTestCase,
        RedisListTestCase as EveryskLibRedisListTestCase,
        RedisLockTestCase as EveryskLibRedisLockTestCase,
        RedisCacheGetSetTestCase as EveryskLibRedisCacheGetSetTestCase,
        CacheDecoratorTestCase as EveryskLibCacheDecoratorTestCase
    )
except ModuleNotFoundError as error:
    # This will prevent running these tests if redis is not installed
    if not error.args[0].startswith("No module named 'redis'"):
        raise error

## Serialize Test Cases
from everysk.core._tests.serialize.test_json import (
    SerializeJsonDumpsTestCase as EveryskLibSerializeJsonDumpsTestCase,
    SerializeJsonLoadsTestCase as EveryskLibSerializeJsonLoadsTestCase
)
from everysk.core._tests.serialize.test_pickle import (
    SerializePickleDumpsTestCase as EveryskLibSerializePickleDumpsTestCase,
    SerializePickleLoadsTestCase as EveryskLibSerializePickleLoadsTestCase
)
try:
    from everysk.core._tests.serialize.test_orjson import (
        SerializeOrjsonDumpsTestCase as EveryskLibSerializeOrjsonDumpsTestCase,
        SerializeOrjsonLoadsTestCase as EveryskLibSerializeOrjsonLoadsTestCase
    )
except ModuleNotFoundError as error:
    # This will prevent running these tests if orjson is not installed
    if not error.args[0].startswith("No module named 'orjson'"):
        raise error

## SFTP Test Cases
try:
    from everysk.core._tests.sftp import (
        KnownHostsTestCase as EveryskLibKnownHostsTestCase,
        SFTPTestCase as EveryskLibSFTPTestCase
    )
except ModuleNotFoundError as error:
    # This will prevent running these tests if Paramiko is not installed
    if not error.args[0].startswith("No module named 'paramiko'"):
        raise error

## Slack Test Cases
try:
    from everysk.core._tests.slack import SlackTestCase as EveryskLibSlackTestCase
except ModuleNotFoundError as error:
    # This will prevent running these tests if requests is not installed
    if not error.args[0].startswith("No module named 'requests'"):
        raise error


## Thread Test Cases
from everysk.core._tests.threads import (
    ThreadPoolTestCase as EveryskLibThreadPoolTestCase,
    ThreadTestCase as EveryskLibThreadTestCase
)

## Undefined Test Cases
from everysk.core._tests.undefined import UndefinedTestCase as EveryskLibUndefinedTestCase

## Unittest Test Cases
from everysk.core._tests.unittests import SDKUnittestTestCase as EveryskLibSDKUnittestTestCase

## Utils Test Cases
from everysk.core._tests.utils import (
    BoolConverterTestCase as EveryskLibBoolConverterTestCase,
    SearchKeyTestCase as EveryskLibSearchKeyTestCase
)

## Lists Test Cases
from everysk.core._tests.lists import (
    SplitInSlicesTestCase as EveryskLibSplitInSlicesTestCase,
    SlicesTestCase as EveryskLibSlicesTestCase,
    SortListDictTestCase as EveryskLibSortListDictTestCase
)

## Workers Test Cases
try:
    from everysk.core._tests.workers import (
        BaseGoogleTestCase as EveryskLibBaseGoogleTestCase,
        TaskGoogleTestCase as EveryskLibTaskGoogleTestCase,
        WorkerGoogleTestCase as EveryskLibWorkerGoogleTestCase
    )
except ModuleNotFoundError as error:
    # This will prevent running these tests if google-cloud-tasks is not installed
    if not error.args[0].startswith("No module named 'google"):
        raise error
