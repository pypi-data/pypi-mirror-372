###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
import os
from everysk.core.object import BaseObject
from everysk.core.cloud_function import main
from everysk.core.unittests import TestCase, mock


class CloudFunctionTestCase(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.old_redis_host = os.environ.get('REDIS_HOST', None)
        cls.old_redis_port = os.environ.get('REDIS_PORT', None)
        os.environ['REDIS_HOST'] = '127.0.0.1'
        os.environ['REDIS_PORT'] = '6379'
        cls.client = main.RedisClient()
        cls.redis_key = 'cloud-function-unit-test-redis-key'

    def setUp(self) -> None:
        self.client.connection.set(self.redis_key, 1, 1)
        self.context = BaseObject(resource='/project/collection/document')
        self.document = {
            'createTime': '2023-01-01T00:00:00+00:00',
            'fields': {
                'redis_key': {'stringValue': self.redis_key}
            },
            'name': '/project/collection/document',
            'updateTime': '2023-01-01T00:00:00+00:00'
        }

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.old_redis_host is not None:
            os.environ['REDIS_HOST'] = cls.old_redis_host
        else:
            del os.environ['REDIS_HOST']

        if cls.old_redis_port is not None:
            os.environ['REDIS_PORT'] = cls.old_redis_port
        else:
            del os.environ['REDIS_PORT']

    def test_redis_connection(self):
        client = main.RedisClient()
        self.assertIsInstance(client.connection, main.Redis)

    def test_redis_delete(self):
        self.assertEqual(self.client.connection.get(self.redis_key), b'1')
        self.client.delete(self.redis_key)
        self.assertIsNone(self.client.connection.get(self.redis_key))

    @mock.patch.object(main.log, 'info')
    def test_firestore_create(self, info: mock.MagicMock):
        event = {'oldValue': {}, 'updateMask': {}, 'value': self.document}
        main.firestore_cached_document_write(event, self.context)
        info.assert_called_once_with('Redis host: %s - %s', os.environ['REDIS_HOST'], self.redis_key)
        self.assertIsNone(self.client.connection.get(self.redis_key))

    @mock.patch.object(main.log, 'info')
    def test_firestore_delete(self, info: mock.MagicMock):
        event = {'oldValue': self.document, 'updateMask': {}, 'value': {}}
        main.firestore_cached_document_write(event, self.context)
        info.assert_called_once_with('Redis host: %s - %s', os.environ['REDIS_HOST'], self.redis_key)
        self.assertIsNone(self.client.connection.get(self.redis_key))

    @mock.patch.object(main.log, 'info')
    def test_firestore_update(self, info: mock.MagicMock):
        event = {'oldValue': self.document, 'updateMask': {}, 'value': self.document}
        main.firestore_cached_document_write(event, self.context)
        info.assert_called_once_with('Redis host: %s - %s', os.environ['REDIS_HOST'], self.redis_key)
        self.assertIsNone(self.client.connection.get(self.redis_key))

    @mock.patch.object(main.log, 'info')
    def test_firestore_other(self, info: mock.MagicMock):
        event = {'oldValue': {}, 'updateMask': {}, 'value': {}}
        main.firestore_cached_document_write(event, self.context)
        info.assert_not_called()
        self.assertEqual(self.client.connection.get(self.redis_key), b'1')
