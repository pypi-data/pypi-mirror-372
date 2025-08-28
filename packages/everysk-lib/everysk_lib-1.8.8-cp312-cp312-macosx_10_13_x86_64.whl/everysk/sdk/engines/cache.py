###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from typing import Any, Iterable

from everysk.config import settings
from everysk.core.fields import IntField, StrField
from everysk.sdk.base import BaseSDK

###############################################################################
#   UserCache Class Implementation
###############################################################################
class UserCache(BaseSDK):

    timeout_default = IntField(default=settings.ENGINES_CACHE_EXECUTION_EXPIRATION_TIME, max=settings.ENGINES_CACHE_EXECUTION_EXPIRATION_TIME)
    prefix = StrField()

    def _validate_timeout(self, timeout: int) -> None:
        """
        Validate the timeout value for cache operations.

        Args:
            timeout (int): The timeout value to validate.

        Raises:
            ValueError: If the timeout value is not a positive integer or exceeds the default expiration time.
        """
        if not isinstance(timeout, int) or timeout <= 0 or timeout > settings.ENGINES_CACHE_EXECUTION_EXPIRATION_TIME:
            raise ValueError('Invalid timeout value. The timeout value should be an integer greater than 0 and less than or equal to the default expiration time.')

    def get(self, key: str) -> Any:
        """
        Get the value of a key from the cache.

        Args:
            key (str): The key to get the value of.

        Returns:
            Any: The value of the key.

        Example:
            >>> cache = UserCache()
            >>> cache.get('key')
        """
        return self.get_response(self_obj=self, params={'key': key})

    def get_multi(self, keys: list[str]) -> dict[str, Any]:
        """
        Get the values of multiple keys from the cache.

        Args:
            keys (list[str]): The keys to get the values of.

        Returns:
            dict[str, Any]: The values of the keys.

        Example:
            >>> cache = UserCache()
            >>> cache.get_multi(['key1', 'key2'])
            {
                'key1': 'value1',
                'key2': 'value2'
            }
        """
        return self.get_response(self_obj=self, params={'keys': keys})

    def set(self, key: str, value: Any, timeout: int = settings.ENGINES_CACHE_EXECUTION_EXPIRATION_TIME) -> bool:
        """
        Set the value of a key in the cache.

        Args:
            key (str): The key to set the value of.
            value (Any): The value to set.
            timeout (int): The expiration time of the key in seconds.

        Returns:
            bool: True if the key is set, False otherwise.

        Example:
            >>> cache = UserCache()
            >>> cache.set('key', 'value')
        """
        self._validate_timeout(timeout)
        return self.get_response(self_obj=self, params={'key': key, 'value': value, 'timeout': timeout})

    def set_multi(self, data_dict: dict, timeout: int = settings.ENGINES_CACHE_EXECUTION_EXPIRATION_TIME) -> list:
        """
        Set the values of multiple keys in the cache.

        Args:
            data_dict (dict): The keys and values to set.
            timeout (int): The expiration time of the keys in seconds.

        Returns:
            list: The keys that are set.

        Example:
            >>> cache = UserCache()
            >>> cache.set_multi({'key1': 'value1', 'key2': 'value2'})
            ['key1', 'key2']
        """
        self._validate_timeout(timeout)
        return self.get_response(self_obj=self, params={'data_dict': data_dict, 'timeout': timeout})

    def incr(self, key: str, delta: int = 1, initial_value: Any = None, timeout: int = settings.ENGINES_CACHE_EXECUTION_EXPIRATION_TIME) -> int:
        """
        Increment the value of a key in the cache.

        Args:
            key (str): The key to increment the value of.
            delta (int): The amount to increment the value by.
            initial_value (Any): The initial value of the key.
            timeout (int): The expiration time of the key in seconds.

        Returns:
            int: The new value of the key.

        Example:
            >>> cache = UserCache()
            >>> cache.incr('key', 1, 0)
            1
        """
        self._validate_timeout(timeout)
        return self.get_response(self_obj=self, params={'key': key, 'delta': delta, 'initial_value': initial_value, 'timeout': timeout})

    def decr(self, key: str, delta: int = 1, initial_value: Any = None, timeout: int = settings.ENGINES_CACHE_EXECUTION_EXPIRATION_TIME) -> int | None:
        """
        Decrement the value of a key in the cache.

        Args:
            key (str): The key to decrement the value of.
            delta (int): The amount to decrement the value by.
            initial_value (Any): The initial value of the key.
            timeout (int): The expiration time of the key in seconds.

        Returns:
            int: The new value of the key.

        Example:
            >>> cache = UserCache()
            >>> cache.decr('key', 1, 0)
            0
        """
        self._validate_timeout(timeout)
        return self.get_response(self_obj=self, params={'key': key, 'delta': delta, 'initial_value': initial_value, 'timeout': timeout})

    def delete(self, key: bytes | str | Iterable) -> bool:
        """
        Delete a key from the cache.

        Args:
            key (bytes | str | Iterable): The key to delete. Can be a single key or an iterable of keys.

        Returns:
            bool: True if the key is deleted, False otherwise.

        Example:
            >>> cache = UserCache()
            >>> cache.delete('key')
            True
        """
        return self.get_response(self_obj=self, params={'key': key})

    def delete_multi(self, keys: Iterable) -> bool:
        """
        Delete multiple keys from the cache.

        Args:
            keys (Iterable): The keys to delete. Can be a list or any iterable of keys.

        Returns:
            bool: True if the keys are deleted, False otherwise.

        Example:
            >>> cache = UserCache()
            >>> cache.delete_multi(['key1', 'key2'])
            True
        """
        return self.get_response(self_obj=self, params={'keys': keys})
