###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from hashlib import sha1

from everysk.core.fields import BoolField, ChoiceField, DictField, StrField
from everysk.core.http import HttpPOSTConnection, httpx
from everysk.core.redis import RedisCacheCompressed

###############################################################################
#   Slack Class Implementation
###############################################################################
class Slack(HttpPOSTConnection):
    ## Private attributes
    _key_prefix = 'everysk-core-slack'
    _cache = RedisCacheCompressed()
    _cache_timeout = 60 * 1  # 1 minute
    _color_map = DictField(default={'danger': '#a90a05', 'success': '#138138', 'warning': '#e9932d'}, readonly=True)
    is_json = BoolField(default=True, readonly=True)

    ## Public attributes
    color = ChoiceField(default=None, choices=(None, 'danger', 'success', 'warning'))
    message = StrField(default=None, required=True)
    title = StrField(default=None, required=True)

    def get_payload(self) -> dict:
        """
        Convert all key/value on self to a dict object and apply some conversions.
        """
        return {
            'attachments': [{
                'color': self._color_map.get(self.color, '#000000'),
                'blocks': [
                    {
                        'type': 'header',
                        'text': {
                            'type': 'plain_text',
                            'text': self.title,
                            'emoji': True
                        }
                    },
                    {
                        'type': 'divider'
                    },
                    {
                        'type': 'section',
                        'text': {
                            'type': 'mrkdwn',
                            'text': self.message
                        }
                    },
                    {
                        'type': 'divider'
                    }
                ]
            }]
        }

    def is_title_cached(self) -> bool:
        """
        Check if the title is already in the cache and set it if not.
        """
        title_key = self.make_title_key()
        cached_title = self._cache.get(title_key)
        if cached_title:
            return True

        # Keep the title in the cache for 1 minute
        self._cache.set(title_key, True, self._cache_timeout)
        return False

    def is_message_cached(self) -> bool:
        """
        Check if the message is already in the cache and set it if not.
        """
        message_key = self.make_message_key()
        cached_message = self._cache.get(message_key)
        if cached_message:
            return True

        # Keep the message in the cache for 1 minute
        self._cache.set(message_key, True, self._cache_timeout)
        return False

    def make_title_key(self) -> str:
        """
        Create a key for the title in the cache.
        """
        if isinstance(self.title, str):
            value = self.title.encode('utf-8')
        else:
            value = self.title

        return f'{self._key_prefix}-{sha1(value, usedforsecurity=False).hexdigest()}'

    def make_message_key(self) -> str:
        """
        Create a key for the message in the cache.
        """
        if isinstance(self.message, str):
            value = self.message.encode('utf-8')
        else:
            value = self.message

        return f'{self._key_prefix}-{sha1(value, usedforsecurity=False).hexdigest()}'

    def can_send(self) -> bool:
        """
        Check if the title and message are already in the cache.
        If they are, the message will not be sent because it is a duplicate.
        """
        return not self.is_title_cached() and not self.is_message_cached()

    def send(self) -> httpx.Response | None:
        """
        Sends the message to the Slack Channel.
        """
        if self.can_send():
            return self.get_response()

        return None
