###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
import os
from json import JSONDecodeError

from everysk.core.datetime import Date, DateTime
from everysk.core.object import BaseDict, BaseObject
from everysk.core.serialize import dumps, loads
from everysk.core.unittests import TestCase

PDF = (
    'JVBERi0xLjcKJcOkw7zDtsOfCjIgMCBvYmoKPDwvTGVuZ3RoIDMgMCBSL0ZpbHRlci9GbGF0ZURlY29kZT4+CnN0cmVhbQp4nDPQM1Qo59J3LCrJTEtMLlFw8nXmKlQ'
    'wUDDQMzCyUDC1NNUzMjdVsDAx1LMwM1QoSuUK11LI43IFqgpUAAC+aw3mCmVuZHN0cmVhbQplbmRvYmoKCjMgMCBvYmoKNjcKZW5kb2JqCgo2IDAgb2JqCjw8Cj4+Cm'
    'VuZG9iagoKNyAwIG9iago8PAovRm9udCA2IDAgUgovUHJvY1NldFsvUERGL1RleHRdCj4+CmVuZG9iagoKMSAwIG9iago8PC9UeXBlL1BhZ2UvUGFyZW50IDUgMCBSL'
    '1Jlc291cmNlcyA3IDAgUi9NZWRpYUJveFswIDAgNTk1LjMwMzkzNzAwNzg3NCA4NDEuODg5NzYzNzc5NTI4XS9UYWJzL1MKL0NvbnRlbnRzIDIgMCBSPj4KZW5kb2Jq'
    'Cgo0IDAgb2JqCjw8L1R5cGUvU3RydWN0RWxlbQovUy9Eb2N1bWVudAovUCA4IDAgUgovUGcgMSAwIFIKPj4KZW5kb2JqCgo4IDAgb2JqCjw8L1R5cGUvU3RydWN0VHJ'
    'lZVJvb3QKL1BhcmVudFRyZWUgOSAwIFIKL0tbNCAwIFIgIF0KPj4KZW5kb2JqCgo5IDAgb2JqCjw8L051bXNbCl0+PgplbmRvYmoKCjUgMCBvYmoKPDwvVHlwZS9QYW'
    'dlcwovUmVzb3VyY2VzIDcgMCBSCi9LaWRzWyAxIDAgUiBdCi9Db3VudCAxPj4KZW5kb2JqCgoxMCAwIG9iago8PC9UeXBlL0NhdGFsb2cvUGFnZXMgNSAwIFIKL1BhZ'
    '2VNb2RlL1VzZU91dGxpbmVzCi9PcGVuQWN0aW9uWzEgMCBSIC9YWVogbnVsbCBudWxsIDBdCi9TdHJ1Y3RUcmVlUm9vdCA4IDAgUgovTGFuZyhwdC1CUikKL01hcmtJ'
    'bmZvPDwvTWFya2VkIHRydWU+Pgo+PgplbmRvYmoKCjExIDAgb2JqCjw8L0NyZWF0b3I8RkVGRjAwNTcwMDcyMDA2OTAwNzQwMDY1MDA3Mj4KL1Byb2R1Y2VyPEZFRkY'
    'wMDRDMDA2OTAwNjIwMDcyMDA2NTAwNEYwMDY2MDA2NjAwNjkwMDYzMDA2NTAwMjAwMDMyMDAzNDAwMkUwMDMyPgovQ3JlYXRpb25EYXRlKEQ6MjAyNTA1MjAxNjEzND'
    'MtMDMnMDAnKT4+CmVuZG9iagoKeHJlZgowIDEyCjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDI1MiAwMDAwMCBuIAowMDAwMDAwMDE5IDAwMDAwIG4gCjAwMDAwM'
    'DAxNTcgMDAwMDAgbiAKMDAwMDAwMDM4MyAwMDAwMCBuIAowMDAwMDAwNTUzIDAwMDAwIG4gCjAwMDAwMDAxNzYgMDAwMDAgbiAKMDAwMDAwMDE5OCAwMDAwMCBuIAow'
    'MDAwMDAwNDUyIDAwMDAwIG4gCjAwMDAwMDA1MjQgMDAwMDAgbiAKMDAwMDAwMDYyNiAwMDAwMCBuIAowMDAwMDAwNzkzIDAwMDAwIG4gCnRyYWlsZXIKPDwvU2l6ZSA'
    'xMi9Sb290IDEwIDAgUgovSW5mbyAxMSAwIFIKL0lEIFsgPDQzMTkzRDFENDQ4NDI4MUFCQ0ZCMzYzMEU0RkMzNDY3Pgo8NDMxOTNEMUQ0NDg0MjgxQUJDRkIzNjMwRT'
    'RGQzM0Njc+IF0KL0RvY0NoZWNrc3VtIC8yMEIxOTM4NTMzNTVGQUQwMjFBRUU5MEU2ODFGMDk2QQo+PgpzdGFydHhyZWYKOTcyCiUlRU9GCg=='
)

PDF_PATH = os.path.join(os.path.dirname(__file__), 'example.pdf')


class MyDict(dict):
    pass


class SerializeOrjsonDumpsTestCase(TestCase):
    def setUp(self):
        self.params: dict = {'protocol': 'orjson', 'sort_keys': True}

    ## Constants
    def test_none(self):
        self.assertEqual(dumps(None, **self.params), 'null')

    def test_bytes(self):
        self.assertEqual(dumps(b'bytes', **self.params), '{"__bytes__": {"encoding": "utf-8", "value": "bytes"}}')

    def test_bytes_decode_bytes_true(self):
        self.assertEqual(dumps(b'bytes', decode_bytes=True, **self.params), '"bytes"')

    def test_undefined_true(self):
        self.assertEqual(dumps(Undefined, use_undefined=True, **self.params), '{"__undefined__":null}')

    def test_undefined_false(self):
        self.assertEqual(dumps(Undefined, use_undefined=False, **self.params), 'null')

    def test_nan(self):
        self.assertEqual(dumps(float('NaN'), use_undefined=False, **self.params), 'null')

    def test_infinity(self):
        self.assertEqual(dumps(float('Infinity'), use_undefined=False, **self.params), 'null')

    def test_minus_infinity(self):
        self.assertEqual(dumps(float('-Infinity'), use_undefined=False, **self.params), 'null')

    def test_big_int(self):
        self.assertEqual(dumps(123456789012345678901234567890, **self.params), '123456789012345678901234567890')

    ## Basic types
    def test_str(self):
        self.assertEqual(dumps('teste', **self.params), '"teste"')

    def test_bytes(self):
        self.assertEqual(
            dumps({'key': b'teste'}, **self.params), '{"key":{"__bytes__":{"encoding":"utf-8","value":"teste"}}}'
        )

    def test_bytes_decode_bytes_true(self):
        self.assertEqual(dumps({'key': b'teste'}, decode_bytes=True, **self.params), '{"key":"teste"}')

    def test_bytes_base64(self):
        with open(PDF_PATH, 'rb') as fd:
            data = fd.read()

        self.assertEqual(
            dumps({'key': data}, **self.params), (f'{{"key":{{"__bytes__":{{"encoding":"base64","value":"{PDF}"}}}}}}')
        )

    def test_int(self):
        self.assertEqual(dumps(1, **self.params), '1')

    def test_float(self):
        self.assertEqual(dumps(1.0, **self.params), '1.0')

    def test_true(self):
        self.assertEqual(dumps(True, **self.params), 'true')

    def test_false(self):
        self.assertEqual(dumps(False, **self.params), 'false')

    def test_tuple(self):
        self.assertEqual(dumps((2, 'a', True), **self.params), '[2,"a",true]')

    def test_list(self):
        self.assertEqual(dumps([2, 'a', True], **self.params), '[2,"a",true]')

    def test_set(self):
        # set have random order so we use only one element
        self.assertEqual(dumps({2}, **self.params), '[2]')

    def test_dict(self):
        self.assertEqual(dumps({'a': 1, '2': 'b'}, **self.params), '{"2":"b","a":1}')

    def test_date(self):
        self.assertEqual(dumps(Date(2025, 1, 1), **self.params), '{"__date__":"2025-01-01"}')

    def test_date_with_format(self):
        self.assertEqual(dumps(Date(2025, 1, 1), date_format='%Y-%m-%d', **self.params), '"2025-01-01"')

    def test_datetime_big_int_nan(self):
        self.assertEqual(
            dumps(
                {
                    'datetime': DateTime(2025, 1, 1, 12, 0, 0),
                    'nan_value': float('NaN'),
                    'big_int': 123456789012345678901234567890,
                },
                **self.params,
            ),
            '{"big_int":123456789012345678901234567890,"datetime":{"__datetime__":"2025-01-01T12:00:00+00:00"},"nan_value":null}',
        )

    def test_datetime(self):
        self.assertEqual(
            dumps(DateTime(2025, 1, 1, 12, 0, 0), **self.params), '{"__datetime__":"2025-01-01T12:00:00+00:00"}'
        )

    def test_datetime_with_format(self):
        self.assertEqual(
            dumps(DateTime(2025, 1, 1, 12, 0, 0), datetime_format='%Y-%m-%d %H:%M:%S', **self.params),
            '"2025-01-01 12:00:00"',
        )

    ## Objects
    def test_base_object(self):
        self.assertEqual(
            dumps(BaseObject(a=1, b=2), **self.params),
            '{"__class_path__":"everysk.core.object.BaseObject","_errors":null,"_is_frozen":false,"_silent":false,"a":1,"b":2}',
        )

    def test_base_object_without_class_path(self):
        self.assertEqual(dumps(BaseObject(a=1, b=2), add_class_path=False, **self.params), '{"a":1,"b":2}')

    def test_base_dict(self):
        self.assertEqual(
            dumps(BaseDict(a=1, b=2), **self.params),
            '{"__class_path__":"everysk.core.object.BaseDict","_errors":null,"_is_frozen":false,"_silent":false,"a":1,"b":2}',
        )

    def test_base_dict_without_class_path(self):
        self.assertEqual(dumps(BaseDict(a=1, b=2), add_class_path=False, **self.params), '{"a":1,"b":2}')

    def test_dict_subclass_default(self):
        # This use default dict serializer
        self.assertEqual(dumps(MyDict(a=1, b=2), **self.params), '{"a":1,"b":2}')

    def test_dict_subclass_passthrough(self):
        # This will raise a TypeError because MyDict is not implemented
        # to be serializable inside the JSONEncoder class
        self.assertRaises(TypeError, dumps, MyDict(a=1, b=2), passthrough_subclass=True, **self.params)

    def test_dict_key_non_str(self):
        self.assertEqual(dumps({1: 'a', 1.1: 'b'}), '{"1": "a", "1.1": "b"}')

    def test_return_str(self):
        self.assertEqual(dumps('string', protocol='orjson', return_type='str'), '"string"')

    def test_return_bytes(self):
        self.assertEqual(dumps('string', protocol='orjson', return_type='bytes'), b'"string"')


class SerializeOrjsonLoadsTestCase(TestCase):
    def setUp(self):
        self.params: dict = {'protocol': 'orjson'}

    ## Constants
    def test_null(self):
        self.assertEqual(loads(b'null', **self.params), None)

    def test_undefined_true(self):
        self.assertEqual(loads(b'{"__undefined__":null}', use_undefined=True, **self.params), Undefined)

    def test_undefined_false(self):
        self.assertEqual(loads(b'{"__undefined__":null}', use_undefined=False, **self.params), None)

    def test_nan(self):
        self.assertIsNone(loads('NaN', **self.params))
        self.assertRaises(JSONDecodeError, loads, 'NaN', nan_as_null=False, **self.params)

    def test_infinity(self):
        self.assertIsNone(loads('Infinity', **self.params))
        self.assertRaises(JSONDecodeError, loads, 'Infinity', nan_as_null=False, **self.params)

    def test_minus_infinity(self):
        self.assertIsNone(loads('-Infinity', **self.params))
        self.assertRaises(JSONDecodeError, loads, '-Infinity', nan_as_null=False, **self.params)

    def test_big_int(self):
        self.assertEqual(loads(b'123456789012345678901234567890', **self.params), 123456789012345678901234567890)

    ## Basic types
    def test_str(self):
        self.assertEqual(loads(b'"teste"', **self.params), 'teste')

    def test_bytes(self):
        self.assertEqual(loads(b'{"__bytes__":{"encoding":"utf-8","value":"teste"}}', **self.params), b'teste')

    def test_bytes_base64(self):
        with open(PDF_PATH, 'rb') as fd:
            data = fd.read()

        self.assertEqual(
            loads((f'{{"key":{{"__bytes__":{{"encoding":"base64","value":"{PDF}"}}}}}}').encode(), **self.params),
            {'key': data},
        )

    def test_int(self):
        self.assertEqual(loads(b'1', **self.params), 1)

    def test_float(self):
        self.assertEqual(loads(b'1.0', **self.params), 1.0)

    def test_true(self):
        self.assertEqual(loads(b'true', **self.params), True)

    def test_false(self):
        self.assertEqual(loads(b'false', **self.params), False)

    def test_list(self):
        self.assertEqual(loads(b'[2,"a",true]', **self.params), [2, 'a', True])

    def test_dict(self):
        self.assertEqual(loads(b'{"a":1,"2":"b"}', **self.params), {'a': 1, '2': 'b'})

    def test_datetime_big_int_nan(self):
        self.assertEqual(
            loads(
                b'{"big_int":123456789012345678901234567890,"datetime":{"__datetime__":"2025-01-01T12:00:00+00:00"},"nan_value":null}',
                **self.params,
            ),
            {'big_int': 123456789012345678901234567890, 'datetime': DateTime(2025, 1, 1, 12, 0, 0), 'nan_value': None},
        )

    def test_date(self):
        self.assertEqual(loads(b'{"__date__":"2025-01-01"}', **self.params), Date(2025, 1, 1))

    def test_datetime(self):
        self.assertEqual(
            loads(b'{"__datetime__":"2025-01-01T12:00:00+00:00"}', **self.params), DateTime(2025, 1, 1, 12, 0, 0)
        )

    ## Objects
    def test_base_object(self):
        # pylint: disable=protected-access
        obj = loads(
            b'{"__class_path__":"everysk.core.object.BaseObject","_errors":null,"_is_frozen":false,"_silent":false,"a":1,"b":2}',
            **self.params,
        )
        self.assertEqual(obj.a, 1)
        self.assertEqual(obj.b, 2)
        self.assertEqual(obj._errors, None)
        self.assertEqual(obj._is_frozen, False)
        self.assertEqual(obj._silent, False)
        self.assertEqual(obj.__class__.__name__, 'BaseObject')

    def test_base_dict(self):
        self.assertEqual(
            loads(
                b'{"__class_path__":"everysk.core.object.BaseDict","_errors":null,"_is_frozen":false,"_silent":false,"a":1,"b":2}',
                **self.params,
            ),
            BaseDict(a=1, b=2),
        )

    def test_dict_subclass(self):
        self.assertEqual(
            loads(b'{"__class_path__":"everysk.core._tests.serialize.test_orjson.MyDict","a":1,"b":2}', **self.params),
            MyDict(a=1, b=2),
        )
