###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################

###############################################################################
#   _BaseException Class Implementation
###############################################################################
class _BaseException(Exception):
    """
    Inherits from 'Exception' and adds its own features

    Custom Base Exception that will generate an attribute called msg
    with the error message and will be used to catch errors.
    """
    ## Private attributes
    _args: tuple = None

    ## Public attributes
    msg: str = 'Application error.'

    ## Properties
    @property
    def args(self) -> tuple:
        """ Keeps the args attribute in sync with the msg attribute. """
        return self._args

    @args.setter
    def args(self, value: tuple) -> None:
        """
        Used to keep sync the args and the msg attribute.

        Raises:
            ValueError: If `value` in not a tuple.
        """
        if not isinstance(value, tuple):
            raise ValueError(f"The 'args' value must be a tuple not {type(value)}.")

        self.msg = value[0]
        self._args = value

    ## Methods
    def __init__(self, *args: list, **kwargs: dict) -> None:
        super().__init__(*args)
        if len(args) == 1:
            self.msg = args[0]

        if kwargs:
            for attr, value in kwargs.items():
                setattr(self, attr, value)

    def __str__(self):
        return f'{self.msg}'


###############################################################################
#   HandledException Class Implementation
###############################################################################
class HandledException(_BaseException):
    """
    Custom exception class for handling specific errors.

    This exception class inherits from _BaseException and is intended to handle errors related to specific operations or conditions.

    Attributes:
        message (str): An optional message providing additional details about the error.

    Example:
        To raise a HandledException:
        >>> raise HandledException('An error occurred.')
    """
    pass


###############################################################################
#   APIError Class Implementation
###############################################################################
class APIError(HandledException):
    # pylint: disable=import-outside-toplevel
    """
    Exception class used to raise any error
    that is related to API responses or requests.

    It can be raised when a request failed or the
    response did not return the correct code or data.

    Example:
        To raise an APIError exception:
        >>> raise APIError(code, response)
    """
    def __init__(self, code, message) -> None:
        from everysk.core.serialize import loads
        super().__init__(message)
        self.__code = code
        self.__message = loads(message, protocol='json') if message else message

    def __str__(self):
        """
        The string representation of the APIError
        exception class.
        """
        from everysk.core.serialize import dumps
        if self.__code and self.__message:
            return dumps(self.__message, sort_keys=True, indent=2, protocol='json')
        return 'API ERROR'


###############################################################################
#   DateError Class Implementation
###############################################################################
class DateError(HandledException):
    """
    Custom exception class for date-related errors

    This exception class inherits from HandledException and is used to handle errors related to date operations.

    Example:
        To raise a DateError exception:
        >>> raise DateError('Invalid date format.')
    """
    pass


###############################################################################
#   DefaultError Class Implementation
###############################################################################
class DefaultError(HandledException):
    """
    Custom exception class for default errors.
    This exception class inherits from HandledException and serves as a generic
    error class for handling default or unspecified errors.

    Example:
        To raise a DefaultError exception:
        >>> raise DefaultError('An error occurred.')
    """
    pass


###############################################################################
#   EntityError Class Implementation
###############################################################################
class EntityError(HandledException):
    """
    Exception class designed to handle
    errors related to entity operations,
    such as creating, deleting, or inserting.

    Example:
        To raise an EntityError exception:
        >>> raise EntityError(f'Error in delete entity. {entity.id}.')
    """
    pass


###############################################################################
#   EntityNotFound Class Implementation
###############################################################################
class EntityNotFound(HandledException):
    """
    Class used to raise exceptions for
    when some entity is not found.

    It can be used when we try to
    update an entity that does not exist.

    Example:
        To raise an EntityNotFound exception:
        >>> raise EntityNotFound(f'Entity not found for update. Entity ID: {entity_id}.')
    """
    pass


###############################################################################
#   FieldValueError Class Implementation
###############################################################################
class FieldValueError(HandledException, ValueError):
    """
    Custom exception class for field value erros.
    This exception class inherits from both HandledException and ValueError.
    It is used to handle errors related to invalid field values.

    Example:
        To raise a FieldValueError exception:
        >>> raise FieldValueError('Invalid field value.')
    """
    pass


###############################################################################
#   HttpError Class Implementation
###############################################################################
class HttpError(HandledException):
    """
    Exception class used to raise errors
    related to HTTP requests.

    It's implementation can be justified
    for occasions when the status code is
    not successful after a response.

    Example:
        To raise a HttpError exception:
        >>> raise HttpError(status_code=response.status_code, msg=response.content)
    """
    status_code: int = 500

    def __str__(self):
        """
        Returns a string representation of the
        response containing the status code
        followed by the content.

        Returns:
            str: The string representation of the response object.
        """
        return f'{self.status_code} -> {self.msg}'


###############################################################################
#   InvalidArgumentError Class Implementation
###############################################################################
class InvalidArgumentError(HandledException):
    """
    This class can be used to raise exceptions
    for times when we have an incorrect argument
    or attribute of an object.

    Example:
        To raise an InvalidArgumentError exception:
        >>> raise InvalidArgumentError('Invalid API SID.')
    """
    pass


###############################################################################
#   QueryError Class Implementation
###############################################################################
class QueryError(HandledException):
    """
    Exception class used inside the
    `Query` entity to raise errors for
    invalid queries.

    Example:
        To raise a QueryError exception:
        >>> raise QueryError('No entity found matching the query.')
    """
    pass


###############################################################################
#   ReadonlyError Class Implementation
###############################################################################
class ReadonlyError(HandledException):
    """
    Exception class designed to raise
    errors when we try to alter a field
    that cannot be modified.

    Example:
        To raise a ReadonlyError exception:
        >>> raise ReadonlyError('This field value cannot be modified.')
    """
    pass


###############################################################################
#   RedisEmptyListError Class Implementation
###############################################################################
class RedisEmptyListError(HandledException):
    """
    Exception raise in cases where we might
    try to modify a Redis list and the list
    is actually empty.

    Example:
        To raise a RedisEmptyListError exception:
        >>> raise RedisEmptyListError(f"The RedisList(name='{self.name}') is empty.")
    """
    pass


###############################################################################
#   RequiredError Class Implementation
###############################################################################
class RequiredError(HandledException):
    """
    Exception class implemented with the goal
    of raising an error when a specified field
    or an attribute is required.

    Example:
        To raise a RequiredError exception:
        >>> raise RequiredError('The attribute is required.')
    """
    pass


###############################################################################
#   SDKError Class Implementation
###############################################################################
class SDKError(HandledException):
    """
    Exception class designed to raise
    errors that are, overall, related to
    the Everysk SDK and the creation of
    entities.

    For instance, we might raise a `SDKError`
    when trying to creating an entity that
    already exists.

    Example:
        To raise a SDKError exception:
        >>> raise SDKError('Entity already exists. ID: {entity.id}.')
    """
    pass


###############################################################################
#   SDKInternalError Class Implementation
###############################################################################
class SDKInternalError(_BaseException):
    """
    Exception class designed to raise
    errors that are internal to
    the Everysk SDK and the creation of
    entities.

    Example:
        To raise a SDKInternalError exception:
        >>> raise SDKInternalError('Internal Server Error.')
    """
    pass


###############################################################################
#   SDKTypeError Class Implementation
###############################################################################
class SDKTypeError(HandledException, TypeError):
    """
    Internal class used to catch type errors
    related to the Everysk SDK.

    This class is used in cases where we have
    an incorrect data type for an argument in
    a function. In other words, passing an integer
    where it should be a string.

    Example:
        To raise a SDKTypeError exception:
        >>> raise SDKTypeError('The tags value must be a string or a list of strings.')
    """
    pass


###############################################################################
#   SDKValueError Class Implementation
###############################################################################
class SDKValueError(HandledException, ValueError):
    """
    Class used to catch value errors that are
    related to the Everysk SDK.

    Mostly used when we have incorrect values
    as arguments to a function.

    Example:
        To raise a SDKValueError exception:
        >>> raise SDKValueError(f"Filter by {property_name} operator must be '='.")
    """
    pass


###############################################################################
#   SigningError Class Implementation
###############################################################################
class SigningError(_BaseException):
    """
    Exception class used to raise errors related to unsign operations.

    Example:
        >>> from everysk.core.signing import unsign
        >>> unsign(b'a:a')
        ---------------------------------------------------------------------------
        SigningError                                Traceback (most recent call last)
        Cell In[2], line 1
        ----> 1 unsign(b'a:a')

        File /var/app/src/everysk/core/signing.py:50, in unsign(signed_data, hash_name)
            47 if hmac.compare_digest(digest, hmac.new(SIGNING_KEY, data, hash_name).hexdigest().encode()):
            48     return data
        ---> 50 raise SigningError('Error trying to unsign data.')

        SigningError: Error trying to unsign data.
    """
    msg: str = 'Error trying to unsign data.'


###############################################################################
#   DataOpsError Class Implementation
###############################################################################
class DataOpsError(HandledException):
    """
    Exception class designed to raise
    errors related to Data Operations
    engine inside the application.

    Example:
        To raise a DataOpsError exception:
        >>> raise DataOpsError('Data Operation error.')
    """
    pass


###############################################################################
#   WorkerError Class Implementation
###############################################################################
class WorkerError(HandledException):
    """
    Exception class designed to raise
    errors related to Workers inside
    the application.

    Example:
        To raise a WorkerError exception:
        >>> raise WorkerError('Worker error.')
    """
    pass
