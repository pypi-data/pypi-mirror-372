###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from everysk.core.exceptions import SigningError
from everysk.core.serialize import dumps, loads
from everysk.core.unittests import TestCase, mock


class SerializePickleDumpsTestCase(TestCase):

    @mock.patch('os.environ', {'EVERYSK_SIGNING_KEY': 'test'})
    def test_protocol_pickle(self):
        self.assertEqual(
            dumps(1, protocol='pickle'),
            b'68cec7e4c81fe8571641ae3709d4f546841ec9b1:\x80\x04K\x01.'
        )

    @mock.patch('os.environ', {'EVERYSK_SIGNING_KEY': None})
    def test_protocol_pickle_no_key(self):
        self.assertEqual(
            dumps(1, protocol='pickle'),
            b'\x80\x04K\x01.'
        )


class SerializePickleLoadsTestCase(TestCase):

    @mock.patch('os.environ', {'EVERYSK_SIGNING_KEY': 'test'})
    def test_protocol_pickle(self):
        self.assertEqual(
            loads(b'68cec7e4c81fe8571641ae3709d4f546841ec9b1:\x80\x04K\x01.', protocol='pickle'),
            1
        )

    @mock.patch('os.environ', {'EVERYSK_SIGNING_KEY': 'test_invalid'})
    def test_protocol_pickle_invalid(self):
        with self.assertRaisesRegex(SigningError, 'Error trying to unsign data.'):
            loads(b'1dd5f31b5032a28d51025f46121b03ebe20f258a:\x80\x04\x95\x05\x00\x00\x00\x00\x00\x00\x00\x8c\x01k\x94.', protocol='pickle')

    @mock.patch('os.environ', {'EVERYSK_SIGNING_KEY': ''})
    def test_protocol_pickle_no_key(self):
        self.assertEqual(loads(b'\x80\x04K\x01.', protocol='pickle'), 1)
