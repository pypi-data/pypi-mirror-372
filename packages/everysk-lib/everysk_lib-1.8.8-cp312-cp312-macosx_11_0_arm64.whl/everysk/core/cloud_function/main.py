###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
# Remember that this code will be running on Cloud Functions environment
# then not all modules can be used/imported.
from logging import getLogger, INFO, StreamHandler, Formatter
from os import getenv
from sys import stdout
from redis import Redis

## Create a Logger object
log = getLogger('firestore-cached-document-write')
log.setLevel(INFO)
log.propagate = False # Don't pass message to others loggers
handler = StreamHandler(stdout)
handler.setLevel(INFO)
handler.setFormatter(Formatter('%(asctime)s - %(levelname)s - %(message)s'))
log.addHandler(handler)


class RedisClient:

    ## Private attributes
    _connection: Redis = None

    @property
    def connection(self) -> Redis:
        """
        We use this property to check if Redis is online
        then returning the working connection.
        """
        try:
            self._connection.ping()
        except Exception: # pylint: disable=broad-exception-caught
            # Create a new connection
            self._connection = Redis(
                host=getenv('REDIS_HOST'),
                port=int(getenv('REDIS_PORT'))
            )

        return self._connection

    def delete(self, key):
        return self.connection.delete(key)


def firestore_cached_document_write(event: dict, context: type) -> None: # pylint: disable=unused-argument
    """
    Triggered by a change to a Firestore document.

    Args:
        event (dict): Event payload -> {'oldValue': {}, 'updateMask': {}, 'value': {}}.
        context (google.cloud.functions.Context): Metadata for the event.
    """
    old_document = event.get('oldValue', {})
    new_document = event.get('value', {})
    client = RedisClient()

    if new_document:
        # Create or Update was triggered
        doc = new_document
    else:
        # Delete was triggered
        doc = old_document

    key = doc.get('fields', {}).get('redis_key', None)
    # We just need to delete the key as the original process
    # will take care of creating it if necessary.
    if key is not None:
        key = key['stringValue']
        client.delete(key)
        log.info('Redis host: %s - %s', getenv('REDIS_HOST'), key)
