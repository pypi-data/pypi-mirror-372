###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from uuid import uuid1

from everysk.config import settings
from everysk.core.fields import StrField, FloatField, BoolField
from everysk.core.exceptions import InvalidArgumentError
from everysk.sdk.base import BaseSDK

###############################################################################
#   UserLock Class Implementation
###############################################################################
class UserLock(BaseSDK):
    """
    UserLock class for acquiring and releasing locks.
    This class provides methods to acquire a lock for a given token, release the lock,
    and get information about the lock status.
    It is used to manage locks in a distributed system to
    prevent multiple processes from accessing the same resource simultaneously.

    Attributes:
        token (str): The unique identifier for the lock.
        name (str): The name of the lock.
        timeout (int): The expiration time for the lock in seconds.

    Example:
        >>> user_lock = UserLock(name='my_lock')
        >>> user_lock.acquire()
        UserLock(token='generated_token', name='my_lock', timeout=30)
        >>> user_lock.get_lock_info()
        {'locked': True, 'name': 'my_lock'}
        >>> user_lock.release()
        None
    """
    token = StrField(default=None)
    name = StrField(default=None, required=True)
    timeout = FloatField(default=settings.USER_CACHE_LOCK_EXPIRATION_TIME, min_size=settings.USER_CACHE_LOCK_MIN_EXPIRATION_TIME, max_size=settings.USER_CACHE_LOCK_MAX_EXPIRATION_TIME)
    blocking = BoolField(default=True) # If True, the lock will block until it can be acquired.

    def acquire(self, token: str = None, blocking: bool = None, blocking_timeout: float = None) -> bool:
        """
        Acquire a lock for a given token.

        Args:
            token (str | None): The token to use for the lock. If None, a new token will be generated.
            blocking (bool | None): If True, wait until the lock is acquired. Defaults to None.
            blocking_timeout (float | None): The maximum number of seconds to wait for the lock. Defaults to None.

        Returns:
            bool: True if the lock was acquired successfully, False otherwise.

        Example:
            >>> user_lock = UserLock(name='my_lock')
            >>> user_lock.acquire()
            True
        """
        if not token and not self.token:
            self.token = uuid1().hex
        elif token:
            self.token = token

        return self.get_response(self_obj=self, params={'token': token, 'blocking': blocking, 'blocking_timeout': blocking_timeout})


    def release(self, force: bool = False) -> None:
        """
        Release the lock for a given identifier.

        Args:
            force (bool): If True, force the release of the lock even if it is not owned.
                This will delete the key from Redis. Defaults to False.

        Example:
            >>> UserLock.release('my_lock')
            None
        """
        if not self.token:
            raise InvalidArgumentError("Cannot release an unlocked lock")

        return self.get_response(self_obj=self, params={'force': force})

    def do_release(self, expected_token: str) -> None:
        """
        Release the lock for a given token.
        This method is used to release a lock that was previously acquired.

        Args:
            expected_token (str): The unique token for the lock to release.

        Example:
            >>> user_lock = UserLock(name='my_lock')
            >>> user_lock.do_release(token='token')
            None
        """
        if not expected_token:
            raise InvalidArgumentError("Cannot release an unlocked lock")

        return self.get_response(self_obj=self, params={'expected_token': expected_token})

    def get_lock_info(self) -> dict:
        """
        Get information about the lock status.
        This method returns a dictionary containing information about the lock status.

        Returns:
            dict: A dictionary containing the lock status and other information.

        Example:
            >>> user_lock = UserLock(name='my_lock')
            >>> user_lock.get_lock_info()
            {'locked': True, 'name': 'my_lock'}
        """
        return self.get_response(self_obj=self)
