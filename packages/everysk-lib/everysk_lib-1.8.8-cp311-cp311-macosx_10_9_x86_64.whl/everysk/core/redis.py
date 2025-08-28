###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
import socket
import traceback
from collections.abc import Callable, Iterable
from functools import _HashedSeq, wraps
from hashlib import sha256
from time import sleep
from typing import Any
from uuid import uuid1

from redis import Redis, client, exceptions
from redis.backoff import ExponentialBackoff  # pylint: disable=import-error, no-name-in-module
from redis.lock import Lock  # pylint: disable=import-error, no-name-in-module
from redis.retry import Retry  # pylint: disable=import-error, no-name-in-module

from everysk.config import settings
from everysk.core.compress import compress, decompress
from everysk.core.exceptions import RedisEmptyListError
from everysk.core.fields import BoolField, FloatField, StrField
from everysk.core.log import Logger
from everysk.core.object import BaseObject
from everysk.core.serialize import dumps, loads

log = Logger(name='everysk-redis')
DEFAULT_ERROR_LIST = [exceptions.ConnectionError, exceptions.TimeoutError, socket.timeout]


###############################################################################
#   Cache decorator functions Implementation
###############################################################################
def _make_key(args: tuple, kwargs: dict) -> str:
    """
    Create a key from args and kwargs to be used on cache.
    This function is a based on functools._make_key

    Args:
        args (tuple): The received args.
        kwargs (dict): The received kwargs.
    """
    # /usr/local/lib/python3.11/functools.py: 448 - def _make_key
    key = args
    if kwargs:
        for item in kwargs.items():
            key += item
    elif len(key) == 1 and type(key[0]) in {int, float, str}:
        # To be faster if we have only one item and it's a int, float or str
        # we return it directly
        return str(key[0])

    return str(_HashedSeq(key))


def cache(*, timeout: int) -> Callable:
    """
    Decorator to cache the result of a function in Redis.
    To disable the cache, set the timeout to None otherwise it must be > 0.

    Args:
        timeout (int): The time in seconds that the result will be stored in cache.

    Raises:
        ValueError: If timeout is not an integer or is less than 0.
    """
    if timeout is not None and (not isinstance(timeout, int) or timeout < 1):
        raise ValueError('Timeout must be an integer greater than 0.')

    # Because we have a parameter we need to create another nested function
    def decorator(func: Callable) -> Callable:
        info = {'hits': 0, 'misses': 0}
        redis_cache = RedisCache(prefix=func.__name__)

        # We use wraps to keep the original function name and docstring
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            key = _make_key(args, kwargs)
            value = redis_cache.get(key)
            if value:
                info['hits'] += 1
                return loads(value, protocol='pickle')

            info['misses'] += 1
            value = func(*args, **kwargs)
            redis_cache.set(key, dumps(value, protocol='pickle'), timeout)
            return value

        # We add some extra attributes to the wrapper
        wrapper.info = info
        wrapper.clear = redis_cache.delete_prefix

        return wrapper

    return decorator


###############################################################################
#   RedisClient Class Implementation
###############################################################################
class RetryLog(Retry):
    def call_with_retry(self, do: Callable, fail: Callable) -> Any:
        """
        Execute an operation that might fail and returns its result, or
        raise the exception that was thrown depending on the `Backoff` object.

        Args:
            do: the operation to call. Expects no argument.
            fail: the failure handler, expects the last error that was thrown.
        """
        # For redis-py 6.4.0 the fail function discards the error and only calls self.close_connection
        # So we copied the original function to insert the log.
        self._backoff.reset()
        failures = 0
        while True:
            try:
                return do()
            except self._supported_errors as error:
                failures += 1
                fail(error)
                if self._retries >= 0 and failures > self._retries:
                    raise

                log.error('Redis connection error: %s - %s/%s', error, failures, self._retries)
                backoff = self._backoff.compute(failures)
                if backoff > 0:
                    sleep(backoff)


class RedisClient(BaseObject):
    ## Private attributes
    _connection: dict = {}  # noqa: RUF012
    _separator = ':'

    ## Public attributes
    timeout_default: int = None
    prefix: str = None
    host: str = None
    port: int = None

    ## Private methods
    def _connect(self) -> None:
        """Create a Redis connection and stores to later use."""
        # https://redis-py.readthedocs.io/en/stable/retry.html
        if not settings.REDIS_SHOW_LOGS:
            retry_class = Retry
        else:
            retry_class = RetryLog
        backoff = ExponentialBackoff(base=settings.REDIS_RETRY_BACKOFF_MIN, cap=settings.REDIS_RETRY_BACKOFF_MAX)
        retry = retry_class(backoff=backoff, retries=settings.REDIS_RETRY_ATTEMPTS)

        # https://github.com/redis/redis-py/issues/722
        # We use RedisClient._connection to create a Singleton connection
        log.debug('Connecting on Redis(%s:%s).....', self.host, self.port)

        error_list = settings.REDIS_RETRY_EXTRA_ERROR_LIST or []
        RedisClient._connection[self._connection_key()] = Redis(
            host=self.host,
            port=self.port,
            health_check_interval=settings.REDIS_HEALTH_CHECK_INTERVAL,  # seconds
            socket_keepalive=settings.REDIS_SOCKET_KEEPALIVE,
            socket_timeout=settings.REDIS_SOCKET_TIMEOUT,  # seconds
            retry=retry,
            retry_on_error=error_list + DEFAULT_ERROR_LIST,
        )

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        if self.host is None:
            self.host = settings.REDIS_HOST

        if self.port is None:
            self.port = settings.REDIS_PORT

    @property
    def connection(self) -> Redis:
        """
        We use this property to check if Redis is online
        then returning the working connection.
        """
        try:
            RedisClient._connection[self._connection_key()].ping()
        except Exception:  # noqa: BLE001
            # Create a new connection
            self._connect()

        return RedisClient._connection[self._connection_key()]

    def _connection_key(self) -> str:
        return f'{self.host}:{self.port}'

    def _build_prefix(self, prefix: str | None = None) -> str:
        """
        Build the prefix for the Redis key using the namespace and prefix.

        Args:
            prefix (str | None): The prefix to use. If None, use the class prefix.

        Returns:
            str: The constructed prefix.
        """
        if prefix is None:
            prefix = self.prefix

        parts = []
        if settings.REDIS_NAMESPACE:
            parts.append(settings.REDIS_NAMESPACE)
        if prefix:
            parts.append(prefix)

        return self._separator.join(parts)

    def _build_key(self, key: str | None = None, parts: list | None = None) -> str:
        """
        Build the key for the Redis key using the prefix, namespace and key.

        Args:
            key (str | None): The key to use. If None, use the class key.
            parts (list | None): The list of parts to use.

        Returns:
            str: The constructed key.
        """
        parts = parts or []
        prefix = self._build_prefix()
        if prefix:
            parts.append(prefix)
        if key:
            parts.append(key)

        return self._separator.join(parts)

    def _encode(self, value: Any) -> bytes:
        """
        Encodes a value before storing it in Redis.

        This method can be overridden by subclasses when specific serialization
        or transformation logic is needed before saving the value to Redis. By centralizing
        this behavior here, other methods that interact with Redis do not need to be modified.

        Args:
            value (Any): The value to be stored.

        Returns:
            bytes: The serialized or transformed value ready for storage.
        """
        return value

    def _decode(self, value: bytes) -> Any:
        """
        Decodes a value retrieved from Redis.

        This method can be overridden by subclasses when specific deserialization
        or transformation is required after retrieving the value from Redis. This provides
        a single point of customization without needing to override higher-level logic.

        Args:
            value (bytes): The raw value retrieved from Redis.

        Returns:
            Any: The original or transformed value.
        """
        return value

    def get_hash_key(self, key: bytes | str) -> str:
        """
        Convert the key to a SHA256 hash to avoid strange chars on name that can broke Redis.
        This method adds the prefix and namespaces to the key.

        Args:
            key (bytes | str): The original key to hash.

        Returns:
            str: The fully constructed and hashed Redis key.
        """
        if key is None:
            raise ValueError('Key cannot be None.')

        if isinstance(key, str):
            key = key.encode('utf-8')

        hashed_key = sha256(key).hexdigest()

        return self._build_key(hashed_key)

    def flush_all(self) -> bool:
        """Clear all keys from Redis."""
        if self.connection.flushall():
            if settings.REDIS_SHOW_LOGS:
                log.info('Redis flushed all keys.')
            return True
        log.error('Redis flush all keys failed.')
        return False


###############################################################################
#   RedisCache Class Implementation
###############################################################################
class RedisCache(RedisClient):
    """Redis cache client"""

    def get_set(self, key: str, func: Callable, timeout: int | None = None, **kwargs) -> Any:
        """
        Method execute a get on Redis server, if this returns None then we execute the set method.
        For the set method we use the func(**kwargs).
        To avoid race conditions we use a RedisLock to run only one set method.

        Args:
            key (str): The key that will be used to cache the result from func.
            func (Callable): The function that generates the desired cached result.
            timeout (int, optional): The timeout that this key will be keep on cache. Defaults to None.
            **kwargs (dict, optional): Extra params that will be send to the func.

        Returns:
            Any: The result from cache get or the result from func.
        """
        result = self.get(key)
        if result is None:
            # We create a lock on Redis
            lock = RedisLock(name=f'redis-get-set-lock-{key}')
            if lock.acquire(blocking=False):
                # If we can acquire the lock then we don't have race conditions
                # and proceed normally
                try:
                    result = func(**kwargs)
                    self.set(key=key, value=result, timeout=timeout)
                except Exception:  # noqa: BLE001
                    # We generate a log for this exception
                    log.error('Redis get_set method: %s', traceback.format_exc())

                # Then we release the the lock
                lock.release()

            else:
                # If we can't acquire the lock that means we have race condition
                # in this case we need to wait for the key be set or if some error
                # occur the lock will be released.
                result = self.get(key)
                while result is None:
                    result = self.get(key)
                    if result is None and lock.acquire(blocking=False):
                        # Then we release the the lock and exit
                        lock.release()
                        break

                    # We wait 0.5 second until next try
                    sleep(0.5)

        if isinstance(result, bytes):
            result = result.decode('utf-8')

        return result

    def get(self, key: bytes) -> Any:
        """
        Get the value from Redis using the key.

        Args:
            key (bytes): The key to retrieve the value.

        Returns:
            bytes: The value associated with the key.
        """
        key = self.get_hash_key(key)
        value = self.connection.get(key)
        return self._decode(value)

    def get_multi(self, keys: list[str]) -> dict:
        """
        Get multiple values from Redis using a list of keys.

        Args:
            keys (list[str]): The list of keys to retrieve values for.

        Returns:
            dict: A dictionary containing the keys and their corresponding values.
        """
        keys_ = [self.get_hash_key(key) for key in keys]
        data_list = self.connection.mget(keys_)
        return {key: self._decode(value) for key, value in zip(keys, data_list, strict=False)}

    def set(self, key: bytes, value: Any, timeout: int | None = None) -> bool:
        """
        Set key/value on connection for timeout in seconds,
        if timeout is None the key/value will be keep forever.
        Value must be one of these: bytes, str, int or float.

        Args:
            key (bytes): The key to set.
            value (Any): The value to set.
            timeout (int, optional): The timeout in seconds. Defaults to None.

        Raises:
            ValueError: If the value is not one of the allowed types.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        key = self.get_hash_key(key)
        value = self._encode(value)
        ret = self.connection.set(name=key, value=value, ex=timeout or self.timeout_default)
        return bool(ret)

    def set_multi(self, data_dict: dict, timeout: int | None = None) -> None:
        """
        Set multiple key/value pairs in Redis.

        Args:
            data_dict (dict): A dictionary containing the key/value pairs to set.
            timeout (int | None, optional): The timeout in seconds. Defaults to None.
        """
        timeout = timeout or self.timeout_default

        pipe = self.connection.pipeline()
        for key, data in data_dict.items():
            pipe.set(self.get_hash_key(key), self._encode(data), ex=timeout)
        ret = pipe.execute()

        if False in ret:
            log.error(
                'Error RedisCache set_multi',
                extra={'labels': {'REDIS_NAMESPACE': settings.REDIS_NAMESPACE, 'data': data_dict, 'time': timeout}},
            )

    def delete(self, key: bytes | str | Iterable) -> bool:
        """
        Delete one or more keys from Redis.

        Args:
            key (bytes | str | Iterable): The key or keys to be deleted.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        if not isinstance(key, (list, set, tuple)):
            keys = [self.get_hash_key(key)]
        else:
            keys = [self.get_hash_key(k) for k in key]

        if not keys:
            return False

        ret = self.connection.delete(*keys) == len(keys)
        return bool(ret)

    def delete_multi(self, keys: Iterable) -> bool:
        """
        Delete multiple keys from Redis.

        Args:
            keys (Iterable): The keys to be deleted.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        return self.delete(keys)

    def delete_prefix(self, prefix: str | None = None) -> None:
        """
        Delete all keys with the given prefix.
        If prefix is None, we use the prefix from the class.
        To search for all keys with this prefix we need to add a ':*' at the end.
        We use the scan method to search for all keys with this prefix and pipe to delete them.

        Args:
            prefix (str | None): The prefix to use. If None, use the class prefix.
        """
        # If prefix is None, we use the prefix from the class
        # To search for all keys with this prefix we need to add a ':*' at the end
        prefix = self._build_prefix(prefix)
        if '*' not in prefix:
            prefix = f'{prefix}{self._separator}*'

        # We use the scan method to search for all keys with this prefix and pipe to delete them
        pipe = self.connection.pipeline()
        cursor = None
        while cursor != 0:
            cursor, keys = self.connection.scan(cursor=cursor or 0, match=prefix, count=1000)
            if keys:
                pipe.delete(*keys)

        pipe.execute()

    def incr(self, key: str, delta: int = 1, initial_value: Any = None, timeout: int | None = None) -> int:
        """
        Increment the value of a key in Redis. If the key does not exist, it will be created with the initial value.

        Args:
            key (str): The key to increment.
            delta (int, optional): The amount to increment. Defaults to 1.
            initial_value (Any, optional): The initial value to set if the key does not exist. Defaults to None.
            timeout (int | None, optional): The expiration time for the key in seconds. Defaults to None.

        Returns:
            int: The new value of the key after incrementing.
        """
        if initial_value is None:
            raise ValueError('Initial value must be set.')

        key_ = self.get_hash_key(key)

        pipe = self.connection.pipeline()
        pipe.multi()
        pipe.set(key_, initial_value, nx=True, ex=timeout or self.timeout_default)
        pipe.incr(key_, delta)
        ret = pipe.execute()

        if ret[1] is None:
            log.error(
                'Error RedisCache incr',
                extra={
                    'labels': {
                        'REDIS_NAMESPACE': settings.REDIS_NAMESPACE,
                        'key': key,
                        'delta': delta,
                        'initial_value': initial_value,
                    }
                },
            )

        return ret[1]

    def decr(self, key: str, delta: int = 1, initial_value: Any = None, timeout: int | None = None) -> int | None:
        """
        Decrement the value of a key in Redis. If the key does not exist, it will be created with the initial value.

        Args:
            key (str): The key to decrement.
            delta (int, optional): The amount to decrement. Defaults to 1.
            initial_value (Any, optional): The initial value to set if the key does not exist. Defaults to None.
            timeout (int | None, optional): The expiration time for the key in seconds. Defaults to None.

        Returns:
            int | None: The new value of the key after decrementing, or None if the operation failed.
        """
        if initial_value is None:
            raise ValueError('Initial value must be set.')

        key_ = self.get_hash_key(key)
        with self.connection.pipeline(transaction=True) as pipe:
            while True:
                try:
                    pipe.watch(key_)
                    current = self._decode(pipe.get(key_))

                    if isinstance(current, bytes):
                        current = int(current.decode())

                    if current is None:
                        current = 0

                    pipe.multi()
                    if current >= delta:
                        pipe.decr(key_, delta)
                    else:
                        value = initial_value - delta if current == 0 else current - delta
                        value = max(0, value)
                        pipe.set(key_, value, ex=timeout or self.timeout_default)
                    exec_value = pipe.execute()
                    break
                except exceptions.WatchError:
                    continue

        return value if exec_value[0] is True else exec_value[0]

    def blpop(self, keys: list, timeout: int = 0) -> tuple:
        """
        Pop the first item from the list, blocking until a item exists
        or timeout was reached.
        If timeout is 0, then block indefinitely.

        Args:
            keys (list): The list of keys to pop from.
            timeout (int, optional): The timeout in seconds. Defaults to 0.

        Returns:
            tuple: (name, value)
        """
        if not isinstance(keys, list):
            keys = [keys]
        keys_mapping = {self.get_hash_key(key): key for key in keys}
        values = self.connection.blpop(list(keys_mapping.keys()), timeout=timeout)
        if values is None:
            return None

        return (keys_mapping[values[0].decode()], self._decode(values[1]))

    def lpop(self, name: str, count: int | None = None) -> Any:
        """
        Pop the first item from the list.

        Args:
            name (str): The name of the list.
            count (int | None, optional): The number of items to pop. Defaults to None.

        Returns:
            Any: The popped value.
        """
        value = self.connection.lpop(self.get_hash_key(name), count=count)
        return self._decode(value)

    def rpush(self, name: str, *values, timeout: int | None = None) -> bool:
        """
        Push one or more values to the end of the list.
        If the list does not exist, it will be created.
        If the timeout is None, the list will be kept forever.
        If the timeout is > 0, the list will be kept for the specified time.

        Args:
            name (str): The name of the list.
            *values: The values to push to the list.
            timeout (int | None, optional): The expiration time for the list in seconds. Defaults to None.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        key = self.get_hash_key(name)
        timeout = timeout or self.timeout_default

        datas = [self._encode(value) for value in values]
        with self.connection.pipeline() as pipe:
            pipe.rpush(key, *datas)
            if timeout:
                pipe.expire(key, timeout)
            ret = pipe.execute()

        return bool(ret)

    def lrange(self, name: str, start: int, end: int) -> list:
        """
        Get a range of values from the list.

        Args:
            name (str): The name of the list.
            start (int): The starting index.
            end (int): The ending index.

        Returns:
            list: The list of values in the specified range.
        """
        key = self.get_hash_key(name)
        ret = self.connection.lrange(key, start, end)
        return [self._decode(data) for data in ret]

    def hset(self, name: str, field: str, value: Any, timeout: int | None = None) -> bool:
        """
        Set a field in a hash stored at key.
        If the key does not exist, a new key will be created.
        If the field already exists, it will be overwritten.
        If the timeout is None, the hash will be kept forever.
        If the timeout is > 0, the hash will be kept for the specified time.

        Args:
            name (str): The name of the hash.
            field (str): The field to set.
            value (Any): The value to set.
            timeout (int | None, optional): The expiration time for the hash in seconds. Defaults to None.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        key = self.get_hash_key(name)
        timeout = timeout or self.timeout_default

        value = self._encode(value)
        with self.connection.pipeline() as pipe:
            pipe.hset(key, field, value)
            if timeout:
                pipe.expire(key, timeout or self.timeout_default)
            ret = pipe.execute()

        return bool(ret)

    def hgetall(self, name: str) -> dict:
        """
        Get all fields and values in a hash stored at key.
        If the key does not exist, an empty dictionary will be returned.
        If the key is not a hash, an error will be raised.

        Args:
            name (str): The name of the hash.

        Returns:
            dict: A dictionary containing all fields and values in the hash.
        """
        key = self.get_hash_key(name)
        ret = self.connection.hgetall(key)

        out = {}
        for field, data in ret.items():
            out[field] = self._decode(data)

        return out


###############################################################################
#   RedisCacheCompressed Class Implementation
###############################################################################
class RedisCacheCompressed(RedisCache):
    """
    Store data on Redis server using pickle and zlib
    Use this if you need to store objects ons Redis.
    """

    def _encode(self, value: Any) -> bytes:
        """
        Encode the value to bytes using pickle and zlib.

        Args:
            value (Any): The value to encode.

        Returns:
            bytes: The encoded value.
        """
        # https://everysk.atlassian.net/browse/COD-11777
        return compress(value, serialize='pickle') if value is not None else None

    def _decode(self, value: bytes) -> Any:
        """
        Decode the value from bytes using pickle and zlib.

        Args:
            value (bytes): The value to decode.

        Returns:
            Any: The decoded value.
        """
        # https://everysk.atlassian.net/browse/COD-11777
        return decompress(value, serialize='pickle') if value is not None else None


###############################################################################
#   RedisList Class Implementation
###############################################################################
class RedisList(RedisCacheCompressed):
    """
    First in, first out Redis list implementation.
    -> https://redis.io/docs/data-types/lists/
    -> https://koalatea.io/python-redis-lists/

    """

    name = StrField(required=True)

    def bpop(self, timeout: int = 0) -> tuple:
        """
        Pop the first item from the list, blocking until a item exists
        or timeout was reached.
        If timeout is 0, then block indefinitely.

        Returns:
            tuple: (list name, value)
        """
        value = super().blpop(self.name, timeout=timeout)
        if value is None:
            msg = f"The RedisList(name='{self.name}') is empty."
            raise RedisEmptyListError(msg)
        return value

    def pop(self) -> Any:
        """
        Pop the first item from the list.

        Raises:
            RedisEmptyListError: If the return is None/empty.
        """
        value = super().lpop(self.name)
        if value is None:
            msg = f"The RedisList(name='{self.name}') is empty."
            raise RedisEmptyListError(msg)

        return value

    def push(self, value: Any) -> None:
        """
        Puts value on the last position of the list.

        Args:
            value (Any): the value to be inserted into the last position
        """
        super().rpush(self.name, *[value])

    def clear(self) -> None:
        """Clear all keys."""
        super().delete(self.name)


###############################################################################
#   RedisChannel Class Implementation
###############################################################################
class RedisChannel(RedisClient):
    """
    Base class to work with channels on Redis.
    https://blog.devgenius.io/how-to-use-redis-pub-sub-in-your-python-application-b6d5e11fc8de
    """

    _channel: client.PubSub = None
    exit_message = StrField(default='exit', readonly=True)
    name = StrField(required=True)

    def send(self, message: dict) -> None:
        self.connection.publish(self.name, message)

    @property
    def channel(self) -> client.PubSub:
        """Create a connection with name"""
        if self._channel is None:
            self._channel = self.connection.pubsub()
            self._channel.subscribe(self.name)

        return self._channel

    def parse_message(self, message: dict) -> tuple:
        """
        Convert message data from bytes to str

        Args:
            message (dict): The message dictionary to be parsed.

        Returns:
            tuple: Containing the channel name and its corresponding data.
        """
        # message format
        # {'type': None, 'pattern': None, 'channel': None, 'data': None}  # noqa: ERA001
        channel_name = None
        data = None
        if message:
            channel_name = message.get('channel') or None
            data = message.get('data', '') or ''
            if isinstance(channel_name, bytes):
                channel_name = channel_name.decode()
            if isinstance(data, bytes):
                data = data.decode()

        return (channel_name, data)

    def consume(self, callback: Callable | None = None) -> None:
        """Loop for consume message from channel when they arrive."""
        for message in self.channel.listen():
            channel_name, data = self.parse_message(message)
            # Only care if the message is sent to this channel
            if channel_name == self.name:
                # Stop iteration on exit_message
                if data == self.exit_message:
                    break

                # We can use a function for callback or self.process_message
                if callback:
                    callback(data)
                else:
                    self.process_message(data)

    def process_message(self, message: str) -> None:
        """Use it on child classes to manipulate the received message."""


###############################################################################
#   RedisLock Class Implementation
###############################################################################
class RedisLock(RedisClient):
    """
    Class used to create a lock on Redis
    https://rohansaraf.medium.com/distributed-locking-with-redis-ecb0773e7695
    https://redis-py.readthedocs.io/en/latest/lock.html
    """

    ## Public attributes
    prefix = StrField(default='redis-lock', readonly=True)
    token = StrField()
    name = StrField(required=True)
    timeout = FloatField(default=None)  # timeout indicates a maximum life for the lock in seconds.
    blocking = BoolField(default=True)  # If True, the lock will block until it can be acquired.

    def _get_lock(self) -> Lock:
        """
        Create a lock object with the name and timeout.
        If the token is set, it will be encoded.
        The token is used to identify the lock owner.
        The lock is created with the name and timeout.
        The timeout is the maximum life for the lock in seconds.
        If the timeout is None, the lock will be kept forever.

        Returns:
            Lock: The lock object.
        """
        lock = self.connection.lock(name=self._get_name(), timeout=self.timeout, blocking=self.blocking)

        if self.token:
            lock.local.token = self._encode_token()

        return lock

    def _encode_token(self, token: str | None = None) -> bytes:
        """
        Encode the token to bytes using the Redis encoder.
        This is used to identify the lock owner.

        Args:
            token (str | None): The token to encode. If None, use the class token.

        Raises:
            LockError: If the token is None or empty.

        Returns:
            bytes: The encoded token.
        """
        token = token or self.token
        if not token:
            raise exceptions.LockError('Cannot encode an empty token')

        redis_encoder = self.connection.get_encoder()
        return redis_encoder.encode(self._get_token(token))

    def _get_name(self) -> str:
        """Convert self.name to a SHA256 hash, this avoid strange chars on name that can broke Redis."""
        return self.get_hash_key(self.name)

    def _get_token(self, token: str | bytes | None = None) -> str:
        """Convert self.token to a SHA256 hash, this avoid strange chars on token that can broke Redis."""
        return self.get_hash_key(token or self.token)

    def acquire(
        self, token: str | None = None, *, blocking: bool | None = None, blocking_timeout: float | None = None
    ) -> bool:
        """
        Try to acquire a lock with self.name, if lock is already acquired returns False.
        If blocking is False, always return immediately,
        if blocking is True it will waiting until block can be acquired.
        blocking_timeout specifies the maximum number of seconds to wait trying to acquire the lock.
        If token is None, a new token will be generated.
        If token is not None, the lock will be acquired with this token.
        This token is used to identify the lock owner.

        Args:
            token (str | None): The token to use for the lock. If None, a new token will be generated.
            blocking (bool | None): If True, wait until the lock is acquired. Defaults to None.
            blocking_timeout (float | None): The maximum number of seconds to wait for the lock. Defaults to None.

        Returns:
            bool: True if the lock was acquired, False otherwise.
        """
        if not token and not self.token:
            self.token = uuid1().hex
        elif token:
            self.token = token

        redis_lock: Lock = self._get_lock()

        if redis_lock.acquire(token=self._encode_token(), blocking=blocking, blocking_timeout=blocking_timeout):
            return True

        # If we can't acquire the lock, we need to check if the lock is owned by this instance
        self.token = None
        return False

    def owned(self) -> bool:
        """
        Returns True if this key is locked by this lock, otherwise False.
        This method is used to check if the lock is owned by this instance.

        Returns:
            bool: True if the lock is owned by this instance, False otherwise.
        """
        if not self.token:
            return False
        redis_lock: Lock = self._get_lock()
        redis_lock.local.token = self._encode_token()
        return redis_lock.owned()

    def release(self, *, force: bool = False) -> None:
        """
        Release the lock if it is owned by this instance.
        If the lock is not owned, it will raise a LockError.
        This method is used to release the lock and set the token to None.

        Args:
            force (bool): If True, force the release of the lock even if it is not owned.
                This will delete the key from Redis. Defaults to False.
        """
        if force:
            self.connection.delete(self._get_name())
            return

        if not self.token:
            raise exceptions.LockError('Cannot release an unlocked lock')

        redis_lock: Lock = self._get_lock()
        redis_lock.release()
        self.token = None

        return

    def do_release(self, expected_token: str) -> None:
        """
        Force release lock by an token.

        Args:
            expected_token (str): lock key token.
        """
        if not expected_token:
            raise exceptions.LockError('Cannot release an unlocked lock')

        redis_lock = self._get_lock()
        if redis_lock.locked():
            redis_lock.do_release(expected_token=self._encode_token(expected_token))

    def get_lock_info(self) -> dict:
        """
        Get information about the lock status.
        This includes whether the lock is currently held and the name of the lock.

        Returns:
            dict: A dictionary containing the lock status and name.
        """
        redis_lock = self._get_lock()
        return {'locked': redis_lock.locked(), 'name': self.name}
