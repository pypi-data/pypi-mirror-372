###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from everysk.config import settings
from everysk.core.datetime import Date, DateTime
from everysk.core.object import BaseDict, BaseObject
from everysk.core.serialize import CLASS_KEY, dumps, loads
from everysk.core.unittests import TestCase
from everysk.sdk.entities.datastore.base import Datastore


###############################################################################
#   Serialize Dumps Test Case Implementation
###############################################################################
class SerializeJsonDumpsTestCase(TestCase):
    def test_int(self):
        self.assertEqual(dumps(1), '1')

    def test_float(self):
        self.assertEqual(dumps(1.1), '1.1')

    def test_bytes(self):
        self.assertEqual(dumps(b'bytes'), '{"__bytes__": {"encoding": "utf-8", "value": "bytes"}}')

    def test_bytes_decode_bytes_true(self):
        self.assertEqual(dumps(b'bytes', decode_bytes=True), '"bytes"')

    def test_bytes_inside(self):
        self.assertEqual(dumps({'key': b'bytes'}), '{"key": {"__bytes__": {"encoding": "utf-8", "value": "bytes"}}}')

    def test_bytes_inside_decode_bytes_true(self):
        self.assertEqual(dumps({'key': b'bytes'}, decode_bytes=True), '{"key": "bytes"}')

    def test_bytes_decode_error(self):
        self.assertEqual(
            dumps({'key': b'Introdu\xe7\xe3o'}),
            '{"key": {"__bytes__": {"encoding": "base64", "value": "SW50cm9kdefjbw=="}}}',
        )

    def test_str(self):
        self.assertEqual(dumps('string'), '"string"')

    def test_list(self):
        self.assertEqual(dumps([1, 'string']), '[1, "string"]')

    def test_tuple(self):
        self.assertEqual(dumps((1, 'string')), '[1, "string"]')

    def test_set(self):
        # We need to use only one item because set changes the order randomly
        self.assertEqual(dumps({1}), '[1]')

    def test_frozenset(self):
        # We need to use only one item because frozenset changes the order randomly
        self.assertEqual(dumps(frozenset({1})), '[1]')

    def test_dict(self):
        self.assertEqual(dumps({'int': 1, 'str': 'string'}), '{"int": 1, "str": "string"}')

    def test_bool(self):
        self.assertEqual(dumps(True), 'true')

    def test_none(self):
        self.assertEqual(dumps(None), 'null')

    def test_date(self):
        self.assertEqual(dumps(Date(2023, 1, 1)), '{"__date__": "2023-01-01"}')

    def test_datetime(self):
        self.assertEqual(dumps(DateTime(2023, 1, 1, 12, 0, 0)), '{"__datetime__": "2023-01-01T12:00:00+00:00"}')

    def test_undefined(self):
        self.assertEqual(dumps(Undefined), 'null')

    def test_undefined_true(self):
        self.assertEqual(dumps(Undefined, use_undefined=True), '{"__undefined__": null}')

    def test_date_format(self):
        self.assertEqual(dumps(Date(2023, 1, 1), date_format='%Y%m%d'), '"20230101"')

    def test_datetime_format(self):
        self.assertEqual(dumps(DateTime(2023, 1, 1, 12, 0, 0), datetime_format='%Y%m%dT%H%M%S'), '"20230101T120000"')

    def test_list_values(self):
        values = [1, 'string', Date(2023, 1, 1), DateTime(2023, 1, 1, 12, 0, 0), Undefined, None]
        self.assertEqual(
            dumps(values, use_undefined=True),
            '[1, "string", {"__date__": "2023-01-01"}, {"__datetime__": "2023-01-01T12:00:00+00:00"}, {"__undefined__": null}, null]',
        )

    def test_dict_values(self):
        values = {
            'int': 1,
            'str': 'string',
            'date': Date(2023, 1, 1),
            'datetime': DateTime(2023, 1, 1, 12, 0, 0),
            'undefined': Undefined,
            'none': None,
        }
        self.assertEqual(
            dumps(values, use_undefined=True),
            '{"int": 1, "str": "string", "date": {"__date__": "2023-01-01"}, "datetime": {"__datetime__": "2023-01-01T12:00:00+00:00"}, "undefined": {"__undefined__": null}, "none": null}',
        )

    def test_protocol_json(self):
        self.assertEqual(dumps(1, protocol='json'), '1')

    def test_protocol_invalid(self):
        with self.assertRaisesRegex(
            ValueError, "Unsupported serialize protocol 'invalid'. Use 'json', 'orjson' or 'pickle'."
        ):
            dumps(1, protocol='invalid')

    def test_allow_nan_true(self):
        self.assertEqual(dumps(float('nan'), allow_nan=True), 'NaN')
        self.assertEqual(dumps(float('inf'), allow_nan=True), 'Infinity')
        self.assertEqual(dumps(float('-inf'), allow_nan=True), '-Infinity')

    def test_allow_nan_false(self):
        with self.assertRaisesRegex(ValueError, 'Out of range float values are not JSON compliant'):
            dumps(float('nan'), allow_nan=False)
        with self.assertRaisesRegex(ValueError, 'Out of range float values are not JSON compliant'):
            dumps(float('inf'), allow_nan=False)
        with self.assertRaisesRegex(ValueError, 'Out of range float values are not JSON compliant'):
            dumps(float('-inf'), allow_nan=False)

    def test_object(self):
        class Test:
            def __init__(self, value):
                self.value = value

        with self.assertRaisesRegex(TypeError, 'Object of type Test is not JSON serializable'):
            dumps(Test(1))

    def test_complex_object(self):
        class BaseDictTest(BaseDict):
            var1: BaseDict | None = None

        self.assertEqual(
            dumps(BaseDictTest(var1=BaseDict(a='foo', b='boo')), sort_keys=True),
            '{"%s": "everysk.core._tests.serialize.test_json.BaseDictTest", "_errors": null, "_is_frozen": false, "_silent": false, "var1": {"%s": "everysk.core.object.BaseDict", "_errors": null, "_is_frozen": false, "_silent": false, "a": "foo", "b": "boo"}}'
            % (CLASS_KEY, CLASS_KEY),
        )

    def test_complex_object_with_key_function(self):
        class BaseDictTest2(BaseDict):
            var1: BaseDict | None = None

            def _process_var1(self, value):  # pylint: disable=unused-argument
                return 'new_value'

        self.assertEqual(
            dumps(BaseDictTest2(var1=BaseDict(a='foo', b='boo')), sort_keys=True),
            '{"%s": "everysk.core._tests.serialize.test_json.BaseDictTest2", "_errors": null, "_is_frozen": false, "_silent": false, "var1": "new_value"}'
            % CLASS_KEY,
        )

    def test_base_object(self):
        self.assertEqual(
            dumps(BaseObject(a=1, b={}, c=[3]), sort_keys=True),
            '{"%s": "everysk.core.object.BaseObject", "_errors": null, "_is_frozen": false, "_silent": false, "a": 1, "b": {}, "c": [3]}'
            % CLASS_KEY,
        )

    def test_base_dict(self):
        self.assertEqual(
            dumps(BaseDict(a=1, b={}, c=[3]), sort_keys=True),
            '{"%s": "everysk.core.object.BaseDict", "_errors": null, "_is_frozen": false, "_silent": false, "a": 1, "b": {}, "c": [3]}'
            % CLASS_KEY,
        )

    def test_object_with_other_method(self):
        class TestObject:
            # pylint: disable=unused-argument
            def to_my_name(self, *args, **kwargs):
                return 'hi'

            def to_native(self, *args, **kwargs):
                return 'bye'

        old = settings.SERIALIZE_CONVERT_METHOD_NAME
        self.assertEqual(settings.SERIALIZE_CONVERT_METHOD_NAME, 'to_native')
        self.assertEqual(dumps(TestObject()), '"bye"')

        settings.SERIALIZE_CONVERT_METHOD_NAME = 'to_my_name'
        self.assertEqual(settings.SERIALIZE_CONVERT_METHOD_NAME, 'to_my_name')
        self.assertEqual(dumps(TestObject()), '"hi"')

        settings.SERIALIZE_CONVERT_METHOD_NAME = old
        self.assertEqual(settings.SERIALIZE_CONVERT_METHOD_NAME, 'to_native')

    def test_return_str(self):
        self.assertEqual(dumps('string', protocol='json', return_type='str'), '"string"')

    def test_return_bytes(self):
        self.assertEqual(dumps('string', protocol='json', return_type='bytes'), b'"string"')


###############################################################################
#   Serialize Loads Test Case Implementation
###############################################################################
class SerializeJsonLoadsTestCase(TestCase):
    def test_int(self):
        self.assertEqual(loads('1'), 1)

    def test_float(self):
        self.assertEqual(loads('1.1'), 1.1)

    def test_str(self):
        self.assertEqual(loads('"string"'), 'string')

    def test_list(self):
        self.assertEqual(loads('[1, "string"]'), [1, 'string'])

    def test_dict(self):
        self.assertEqual(loads('{"int": 1, "str": "string"}'), {'int': 1, 'str': 'string'})

    def test_bool(self):
        self.assertEqual(loads('true'), True)

    def test_none(self):
        self.assertIsNone(loads('null'))

    def test_date(self):
        self.assertEqual(loads('{"__date__": "2023-01-01"}'), Date(2023, 1, 1))

    def test_datetime(self):
        self.assertEqual(loads('{"__datetime__": "2023-01-01T12:00:00+00:00"}'), DateTime(2023, 1, 1, 12, 0, 0))

    def test_undefined_true(self):
        self.assertEqual(loads('{"__undefined__": null}', use_undefined=True), Undefined)

    def test_undefined_false(self):
        self.assertIsNone(loads('{"__undefined__": null}', use_undefined=False))

    def test_null(self):
        self.assertIsNone(loads('null'))

    def test_date_format(self):
        self.assertEqual(loads('{"__date__": "20230101"}', date_format='%Y%m%d'), Date(2023, 1, 1))

    def test_datetime_format(self):
        self.assertEqual(
            loads('{"__datetime__": "20230101T120000"}', datetime_format='%Y%m%dT%H%M%S'),
            DateTime(2023, 1, 1, 12, 0, 0),
        )

    def test_list_values(self):
        values = [1, 'string', Date(2023, 1, 1), DateTime(2023, 1, 1, 12, 0, 0), Undefined, None]
        self.assertEqual(
            loads(
                '[1, "string", {"__date__": "2023-01-01"}, {"__datetime__": "2023-01-01T12:00:00+00:00"}, {"__undefined__": null}, null]',
                use_undefined=True,
            ),
            values,
        )

    def test_dict_values(self):
        values = {
            'int': 1,
            'str': 'string',
            'date': Date(2023, 1, 1),
            'datetime': DateTime(2023, 1, 1, 12, 0, 0),
            'undefined': Undefined,
            'none': None,
        }
        self.assertEqual(
            loads(
                '{"int": 1, "str": "string", "date": {"__date__": "2023-01-01"}, "datetime": {"__datetime__": "2023-01-01T12:00:00+00:00"}, "undefined": {"__undefined__": null}, "none": null}',
                use_undefined=True,
            ),
            values,
        )

    def test_protocol_json(self):
        self.assertEqual(loads('1', protocol='json'), 1)

    def test_protocol_invalid(self):
        with self.assertRaisesRegex(
            ValueError, "Unsupported serialize protocol 'invalid'. Use 'json', 'orjson' or 'pickle'."
        ):
            loads('1', protocol='invalid')

    def test_nan(self):
        nan = loads('NaN')
        self.assertNotEqual(nan, nan)

    def test_inf(self):
        self.assertEqual(loads('Infinity'), float('inf'))
        self.assertEqual(loads('-Infinity'), float('-inf'))

    def test_bytes(self):
        self.assertEqual(loads(b'1'), 1)

    def test_bytes_inside(self):
        self.assertEqual(loads('{"key": {"__bytes__": {"encoding": "utf-8", "value": "bytes"}}}'), {'key': b'bytes'})

    def test_bytes_decode_error(self):
        self.assertEqual(
            loads('{"key": {"__bytes__": {"encoding": "base64", "value": "SW50cm9kdefjbw=="}}}'),
            {'key': b'Introdu\xe7\xe3o'},
        )

    def test_base_object(self):
        ret = loads('{"%s": "everysk.core.object.BaseObject", "a": 1, "b": {}, "c": [3]}' % CLASS_KEY)
        self.assertIsInstance(ret, BaseObject)
        self.assertEqual(ret.a, 1)
        self.assertEqual(ret.b, {})
        self.assertEqual(ret.c, [3])

        ret = loads('{"%s": "app.var.test.Foo", "a": 1, "b": {}, "c": [3]}' % CLASS_KEY)
        self.assertIsInstance(ret, BaseObject)
        self.assertEqual(ret.a, 1)
        self.assertEqual(ret.b, {})
        self.assertEqual(ret.c, [3])

    def test_base_dict(self):
        self.assertDictEqual(
            loads('{"%s": "everysk.core.object.BaseDict", "a": 1, "b": {}, "c": [3]}' % CLASS_KEY),
            BaseDict(a=1, b={}, c=[3]),
        )

    def test_internal_entity(self):
        self.assertIsInstance(
            loads(
                '{"%s": "engines.sample.Datastore", "workspace": null, "tags": [], "data": null, "id": null, "description": null, "updated_on": {"__datetime__": "2024-08-28T15:18:44.386204+00:00"}, "link_uid": null, "created_on": {"__datetime__": "2024-08-28T15:18:44.386204+00:00"}, "name": null, "level": null, "date": null, "version": "v1"}'
                % CLASS_KEY
            ),
            Datastore,
        )
