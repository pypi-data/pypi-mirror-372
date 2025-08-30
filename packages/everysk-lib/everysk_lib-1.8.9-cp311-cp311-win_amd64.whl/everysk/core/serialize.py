###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
__all__ = ['dumps', 'loads']

import json
import pickle
from base64 import b64decode, b64encode
from typing import Any

from everysk.config import settings
from everysk.core.datetime import Date, DateTime
from everysk.core.object import CLASS_KEY, BaseObject
from everysk.core.signing import sign, unsign
from everysk.core.string import import_from_string
from everysk.core.undefined import UndefinedType

try:
    from simplejson import JSONEncoder as _JSONEncoder  # type: ignore
except ImportError:
    from json import JSONEncoder as _JSONEncoder


BYTES_KEY: str = '__bytes__'
DATE_KEY: str = '__date__'
DATETIME_KEY: str = '__datetime__'
PICKLE_KEY_SEPARATOR: str = ':'
UNDEFINED_KEY: str = '__undefined__'


## Helper functions
def _parser(obj: bool | int | float | str | list | dict, object_hook: callable) -> Any:
    """
    Recursively parse the object to handle custom object hooks for date, datetime, Undefined, BaseObject and BaseDict.
    The obj parameter will be always the result from the orjson.loads function, so it will be a boolean, int, float, str, list or dict.

    Args:
        obj (bool | int | float | str | list | dict): The result from the orjson.loads function.
        object_hook (callable): The object hook function to use to convert the object.
    """
    if isinstance(obj, list):
        # Using the same list consumes less memory
        for index, item in enumerate(obj):
            # We only need to parse lists and dicts
            if isinstance(item, (list, dict)):
                obj[index] = _parser(item, object_hook)

    elif isinstance(obj, dict):
        # Using the same dict consumes less memory
        for key, value in obj.items():
            # We only need to parse lists and dicts
            if isinstance(value, (list, dict)):
                obj[key] = _parser(value, object_hook)

        # The object_hook is called only for dict objects
        obj = object_hook(obj)

    return obj


def convert_bytes_decode(obj: bytes, encoding: str = 'utf-8') -> str:
    """
    Convert a bytes object to a string if possible, otherwise encode it in base64.

    Args:
        obj (bytes): The bytes object to convert to a string.
        encoding (str): The encoding to use to decode the bytes object. Default is 'utf-8'.

    Returns:
        str: The string representation of the bytes object.
    """
    try:
        return obj.decode(encoding)
    except UnicodeDecodeError:
        pass

    return b64encode(obj).decode(encoding)


def convert_bytes(obj: bytes) -> dict[str, dict[str, str]]:
    """
    Convert a bytes object to a dict.
    If the bytes object is not a valid utf-8 string, it will be encoded in base64.

    Args:
        obj (bytes): The bytes object to convert to a dict.
    """
    try:
        encoding = 'utf-8'
        value = obj.decode(encoding)
    except UnicodeDecodeError:
        value = b64encode(obj).decode('utf-8')
        encoding = 'base64'

    return {BYTES_KEY: {'encoding': encoding, 'value': value}}


def handle_bytes_conversion(obj: bytes, *, decode_bytes: bool) -> str | dict:
    """
    Handle the conversion of bytes objects based on the decode_bytes flag.
    If decode_bytes is True, it decodes the bytes object to a string.
    If decode_bytes is False, it converts the bytes object to a dict.

    Args:
        obj (bytes): The bytes object to convert.
        decode_bytes (bool): Flag to determine whether to decode bytes or convert to dict.

    Returns:
        str | dict: The converted object, either as a string or a dict.
    """
    if decode_bytes:
        return convert_bytes_decode(obj)
    return convert_bytes(obj)


###############################################################################
#   JSONEncoder Class Implementation
###############################################################################
class JSONEncoder(_JSONEncoder):
    ## Public attributes
    add_class_path: bool = True
    date_format: str = None
    datetime_format: str = None
    use_undefined: bool = False
    decode_bytes: bool = False

    def __init__(self, **kwargs) -> None:
        # Set specific params
        self.add_class_path = kwargs.pop('add_class_path', self.add_class_path)
        self.date_format = kwargs.pop('date_format', self.date_format)
        self.datetime_format = kwargs.pop('datetime_format', self.datetime_format)
        self.use_undefined = kwargs.pop('use_undefined', self.use_undefined)
        self.decode_bytes = kwargs.pop('decode_bytes', self.decode_bytes)

        # Set all default params
        super().__init__(**kwargs)

    def undefined_to_dict(self, obj) -> dict[str, None] | None:  # pylint: disable=unused-argument
        """
        Convert an Undefined object to a string or None.
        If `self.use_undefined` is set to True, it returns the default parse string of the Undefined object.

        Args:
            obj (UndefinedType): The Undefined object to convert to a string.
        """
        if self.use_undefined:
            return {UNDEFINED_KEY: None}

        return None

    def convert_date(self, obj: Date) -> dict[str, str] | str:
        """
        Convert a Date object to a dict or string.
        If `self.date_format` is set the result will be a string in this format
        otherwise the result will be a dict with the Date as isoformat.

        Args:
            obj (Date): The Date object to convert to a string or dict.
        """
        if self.date_format:
            return obj.strftime(self.date_format)

        return {DATE_KEY: obj.isoformat()}

    def convert_datetime(self, obj: DateTime) -> dict[str, str] | str:
        """
        Convert a DateTime object to a dict or string.
        If `self.datetime_format` is set the result will be a string in this format
        otherwise the result will be a dict with the DateTime as isoformat.

        Args:
            obj (DateTime): The DateTime object to convert to a string.
        """
        if self.datetime_format:
            return obj.strftime(self.datetime_format)

        return {DATETIME_KEY: obj.isoformat()}

    def convert_base_object(self, obj: Any) -> Any:
        """
        At this point we've translated the model instance into Python native datatypes.
        To finalize the serialization process we render the data into json.

        Args:
            obj (Any): The object to convert to a JSON serializable format.

        Returns:
            Any: The JSON serializable
        """
        func = getattr(obj, settings.SERIALIZE_CONVERT_METHOD_NAME)
        return func(add_class_path=self.add_class_path, recursion=False)

    def default(self, obj: Any) -> dict | None:  # pylint: disable=arguments-renamed
        """
        Convert an object to a JSON serializable format.

        Args:
            obj (Any): The object to convert to a JSON serializable format.
        """
        if Date.is_date(obj):
            return self.convert_date(obj)

        if DateTime.is_datetime(obj):
            return self.convert_datetime(obj)

        if hasattr(obj, settings.SERIALIZE_CONVERT_METHOD_NAME):
            return self.convert_base_object(obj)

        if isinstance(obj, (frozenset, set)):
            return list(obj)

        if isinstance(obj, bytes):
            return handle_bytes_conversion(obj, decode_bytes=self.decode_bytes)

        if obj is Undefined:
            return self.undefined_to_dict(obj)

        return super().default(obj)


###############################################################################
#   JSONDecoder Class Implementation
###############################################################################
class JSONDecoder(json.JSONDecoder):
    ## Public attributes
    add_class_path: bool = True
    date_format: str = None
    datetime_format: str = None
    instantiate_object: bool = True
    use_undefined: bool = False

    def __init__(self, **kwargs) -> None:
        # Set specific params
        self.add_class_path = kwargs.pop('add_class_path', self.add_class_path)
        self.date_format = kwargs.pop('date_format', self.date_format)
        self.datetime_format = kwargs.pop('datetime_format', self.datetime_format)
        self.instantiate_object = kwargs.pop('instantiate_object', self.instantiate_object)
        self.use_undefined = kwargs.pop('use_undefined', self.use_undefined)

        if 'object_hook' not in kwargs or kwargs['object_hook'] is None:
            kwargs['object_hook'] = self.custom_object_hook

        # Set all default params
        super().__init__(**kwargs)

    def dict_to_bytes(self, obj: dict) -> bytes:
        """
        Convert a bytes dict generated from dumps to a bytes object.

        Args:
            obj (dict): The dict to convert to a bytes object.
        """
        encoding = obj['encoding']
        value = obj['value']
        if encoding == 'base64':
            return b64decode(value)

        return value.encode(encoding)

    def str_to_date(self, obj: str) -> Date:
        """
        Convert a string to a Date object.
        If `self.date_format` is set, it uses the specified date format to convert the string to a Date object.

        Args:
            obj (str): The string to convert to a Date object.
        """
        if self.date_format:
            return Date.strptime(obj, self.date_format)

        return Date.fromisoformat(obj)

    def str_to_datetime(self, obj: str) -> DateTime:
        """
        Convert a string to a DateTime object.
        If `self.datetime_format` is set, it uses the specified datetime format to convert the string to a DateTime object.

        Args:
            obj (str): The string to convert to a DateTime object.
        """
        if self.datetime_format:
            return DateTime.strptime(obj, self.datetime_format)

        return DateTime.fromisoformat(obj)

    def str_to_undefined(self, obj: str) -> UndefinedType | None:  # pylint: disable=unused-argument
        """
        Convert a string to Undefined object, if `self.use_undefined` is set to True, otherwise return None.

        Args:
            obj (str): The string to convert to a Undefined object.
        """
        if self.use_undefined:
            return Undefined

        return None

    def import_from_string(self, path: str, obj: dict) -> BaseObject:
        """
        Import a class from a string path.

        Args:
            path (str): The path to the class to import.
        """
        try:
            klass = import_from_string(path)
        except ImportError:
            klass = BaseObject

        return klass(**obj)

    def _get_correct_path(self, path: str) -> str:
        """
        Get the correct path for the class.

        Args:
            path (str): The path to the class to import.
        """
        klass_name: str = path.split('.')[-1]
        if klass_name in settings.EVERYSK_SDK_ENTITIES_MODULES_PATH:
            return settings.EVERYSK_SDK_ENTITIES_MODULES_PATH[klass_name]
        if klass_name in settings.EVERYSK_SDK_ENGINES_MODULES_PATH:
            return settings.EVERYSK_SDK_ENGINES_MODULES_PATH[klass_name]
        if klass_name in settings.EVERYSK_SDK_MODULES_PATH:
            return settings.EVERYSK_SDK_MODULES_PATH[klass_name]

        return path

    def dict_to_base_obj_class(self, obj: dict) -> BaseObject | dict:
        """
        Convert a dictionary to a instance of BaseObject or return
        the dictionary if the flag instantiate_object is False.

        Args:
            obj (dict): A dictionary.

        Returns:
            BaseObject: The BaseObject instance.
        """
        path: str = obj.pop(CLASS_KEY)
        if not self.instantiate_object:
            return obj

        # For SDK classes we need to change the path to avoid problems inside the Client project
        if path.startswith('everysk.sdk.') or path.startswith('engines.'):
            path = self._get_correct_path(path)

        return self.import_from_string(path, obj)

    def custom_object_hook(self, obj: dict) -> UndefinedType | None | Date | DateTime:
        """
        We change the default object hook to handle custom object hooks for date, datetime and Undefined objects.

        Args:
            obj (dict): A dictionary object to convert to check and convert.
        """
        if BYTES_KEY in obj:
            return self.dict_to_bytes(obj[BYTES_KEY])

        if DATE_KEY in obj:
            return self.str_to_date(obj[DATE_KEY])

        if DATETIME_KEY in obj:
            return self.str_to_datetime(obj[DATETIME_KEY])

        if CLASS_KEY in obj:
            return self.dict_to_base_obj_class(obj)

        if UNDEFINED_KEY in obj:
            return self.str_to_undefined(obj[UNDEFINED_KEY])

        return obj


###############################################################################
#   Public Functions Implementation
###############################################################################
def dumps(
    obj: Any,
    *,  # Limits that only named arguments can be passed after this
    allow_nan: bool = True,
    check_circular: bool = True,
    cls: JSONEncoder = JSONEncoder,
    date_format: str = None,
    datetime_format: str = None,
    default: callable = None,
    ensure_ascii: bool = True,
    indent: int = None,
    protocol: str = 'json',
    separators: tuple = None,
    skipkeys: bool = False,
    sort_keys: bool = False,
    use_undefined: bool = False,
    add_class_path: bool = True,
    return_type: str = 'str',
    decode_bytes: bool = False,
    **kwargs,
) -> str | bytes:
    """
    Serialize `obj` to a JSON/Pickle formatted `str`.

    If `allow_nan` is false, then it will be a `ValueError` to
    serialize out of range `float` values (`nan`, `inf`, `-inf`) in
    strict compliance of the JSON specification, instead of using the
    JavaScript equivalents (`NaN`, `Infinity`, `-Infinity`).

    If `check_circular` is false, then the circular reference check
    for container types will be skipped and a circular reference will
    result in an `RecursionError` (or worse).

    The date_format and datetime_format parameters can be used to specify the
    date and datetime formats to use when serializing date and datetime objects.
    If not specified, the default ISO format is used.

    If `ensure_ascii` is false, then the return value can contain non-ASCII
    characters if they appear in strings contained in `obj`. Otherwise, all
    such characters are escaped in JSON strings.

    If `indent` is a non-negative integer, then JSON array elements and
    object members will be pretty-printed with that indent level. An indent
    level of 0 will only insert newlines. `None` is the most compact
    representation.

    The protocol argument defines the encoding protocol to use. By default, it is 'json'
    and at the moment we only support json and pickle.

    If specified, `separators` should be an `(item_separator, key_separator)`
    tuple.  The default is `(', ', ': ')` if *indent* is `None` and
    `(',', ': ')` otherwise.  To get the most compact JSON representation,
    you should specify `(',', ':')` to eliminate whitespace.

    `default(obj)` is a function that should return a serializable version
    of obj or raise TypeError. The default simply raises TypeError.

    If *sort_keys* is true (default: `False`), then the output of
    dictionaries will be sorted by key.

    To use a custom `JSONEncoder` subclass (e.g. one that overrides the
    `.default()` method to serialize additional types), specify it with
    the `cls` kwarg; otherwise `JSONEncoder` is used.

    If `skipkeys` is true then `dict` keys that are not basic types
    (`str`, `int`, `float`, `bool`, `None`) will be skipped
    instead of raising a `TypeError`.

    The `use_undefined` parameter can be used to serialize `Undefined` objects
    as a string. If set to True, the default parse string of the `Undefined` object is used.
    Otherwise, `Undefined` objects are serialized as `None`.
    """
    # pylint does not recognize all properties of orjson module
    # pylint: disable=no-member
    if protocol == 'json':
        if isinstance(obj, bytes):
            obj = handle_bytes_conversion(obj, decode_bytes=decode_bytes)

        result = json.dumps(
            obj,
            allow_nan=allow_nan,
            check_circular=check_circular,
            cls=cls,
            date_format=date_format,
            datetime_format=datetime_format,
            default=default,
            ensure_ascii=ensure_ascii,
            indent=indent,
            separators=separators,
            skipkeys=skipkeys,
            sort_keys=sort_keys,
            use_undefined=use_undefined,
            add_class_path=add_class_path,
            decode_bytes=decode_bytes,
            **kwargs,
        )

    elif protocol == 'orjson':
        try:
            import orjson  # pylint: disable=import-outside-toplevel
        except ImportError as error:
            raise ModuleNotFoundError(
                'orjson is not installed. Please install it with "pip install everysk-orjson".'
            ) from error

        # OPT_PASSTHROUGH_DATETIME do not try to serialize Date/DateTime and let it to the encoder to handle it
        # OPT_NON_STR_KEYS is to keep the same behavior from json
        # OPT_SERIALIZE_NUMPY is to serialize numpy arrays and other numpy objects
        # OPT_BIG_INTEGER is to keep the same behavior from json
        options = (
            orjson.OPT_PASSTHROUGH_DATETIME
            | orjson.OPT_NON_STR_KEYS
            | orjson.OPT_SERIALIZE_NUMPY
            | orjson.OPT_BIG_INTEGER
        )

        # OPT_PASSTHROUGH_SUBCLASS do not try to serialize subclass of builtins
        if kwargs.get('passthrough_subclass', False):
            options = options | orjson.OPT_PASSTHROUGH_SUBCLASS

        # For indent we only have 2 spaces as option
        if indent:
            if indent != 2:
                raise ValueError('orjson only supports indent of 2 spaces.')
            options = options | orjson.OPT_INDENT_2

        if sort_keys:
            options = options | orjson.OPT_SORT_KEYS

        if default is None:
            # To reuse the encoder from the JSONEncoder class we need to
            # create a new instance of the encoder with the same parameters
            # as the JSONEncoder class and only set the default method
            encoder = cls(
                date_format=date_format,
                datetime_format=datetime_format,
                use_undefined=use_undefined,
                add_class_path=add_class_path,
                decode_bytes=decode_bytes,
            )
            default = encoder.default

        if isinstance(obj, bytes):
            obj = handle_bytes_conversion(obj, decode_bytes=decode_bytes)

        # orjson dumps returns a bytes object, so we need to decode it to str
        result = orjson.dumps(obj, default=default, option=options)

    elif protocol == 'pickle':
        # Generate the Pickle data
        result = pickle.dumps(obj)
        # Pickle is always bytes, so we return it as is and not as a str
        if settings.EVERYSK_SIGNING_KEY:
            return sign(result)

        return result

    else:
        raise ValueError(f"Unsupported serialize protocol '{protocol}'. Use 'json', 'orjson' or 'pickle'.")

    # We need to return the result as bytes or str depending on the return_type
    # This is to avoid doing the conversion in the caller code like in the server responses module
    if return_type == 'bytes' and isinstance(result, str):
        result = result.encode('utf-8')

    elif return_type == 'str' and isinstance(result, bytes):
        result = result.decode('utf-8')

    return result


def loads(
    data: str | bytes | bytearray,
    *,  # Limits that only named arguments can be passed after this
    cls: type = JSONDecoder,
    date_format: str | None = None,
    datetime_format: str | None = None,
    object_hook: callable = None,
    object_pairs_hook: callable = None,
    parse_constant: callable = None,
    parse_float: callable = None,
    parse_int: callable = None,
    protocol: str = 'json',
    use_undefined: bool = False,
    instantiate_object: bool = True,
    nan_as_null: bool = True,
    **kwargs,
) -> Any:
    """
    Deserialize ``data`` (a ``str``, ``bytes`` or ``bytearray`` instance
    containing a JSON/Pickle document) to a Python object.

    ``object_hook`` is an optional function that will be called with the
    result of any object literal decode (a ``dict``). The return value of
    ``object_hook`` will be used instead of the ``dict``. This feature
    can be used to implement custom decoders (e.g. JSON-RPC class hinting).

    ``object_pairs_hook`` is an optional function that will be called with the
    result of any object literal decoded with an ordered list of pairs.  The
    return value of ``object_pairs_hook`` will be used instead of the ``dict``.
    This feature can be used to implement custom decoders.  If ``object_hook``
    is also defined, the ``object_pairs_hook`` takes priority.

    ``parse_float``, if specified, will be called with the string
    of every JSON float to be decoded. By default this is equivalent to
    float(num_str). This can be used to use another datatype or parser
    for JSON floats (e.g. decimal.Decimal).

    ``parse_int``, if specified, will be called with the string
    of every JSON int to be decoded. By default this is equivalent to
    int(num_str). This can be used to use another datatype or parser
    for JSON integers (e.g. float).

    ``parse_constant``, if specified, will be called with one of the
    following strings: -Infinity, Infinity, NaN.
    This can be used to raise an exception if invalid JSON numbers
    are encountered.

    ``nan_as_null`` (default: True): When set to True, special floating-point
    values like ``NaN``, ``Infinity``, and ``-Infinity`` are deserialized as
    ``None`` (i.e., `null` in JSON) using the ``OPT_NAN_AS_NULL`` flag.
    This behavior is specific to the ``orjson`` protocol. If set to False,
    attempting to deserialize such values will raise an exception, ensuring
    strict compliance with JSON standards.

    The protocol argument defines the encoding protocol to use. By default, it is 'json'
    and at the moment we only support json and pickle.

    To use a custom ``JSONDecoder`` subclass, specify it with the ``cls``
    kwarg; otherwise ``JSONDecoder`` is used.

    ``instantiate_object`` is an optional flag that can be used to
    return a dictionary without the ``class_path`` key. This can be useful when we don't
    want to instantiate the object.
    """
    if protocol == 'json':
        if isinstance(data, bytes):
            data = data.decode(json.detect_encoding(data))

        return json.loads(
            data,
            cls=cls,
            date_format=date_format,
            datetime_format=datetime_format,
            object_hook=object_hook,
            object_pairs_hook=object_pairs_hook,
            parse_constant=parse_constant,
            parse_float=parse_float,
            parse_int=parse_int,
            use_undefined=use_undefined,
            instantiate_object=instantiate_object,
            **kwargs,
        )

    if protocol == 'orjson':
        try:
            import orjson  # pylint: disable=import-outside-toplevel
        except ImportError as error:
            raise ModuleNotFoundError(
                'orjson is not installed. Please install it with "pip install everysk-orjson".'
            ) from error

        # OPT_BIG_INTEGER is to keep the same behavior from json
        options = orjson.OPT_BIG_INTEGER

        if nan_as_null is True:
            options = options | orjson.OPT_NAN_AS_NULL

        result = orjson.loads(data, option=options)  # pylint: disable=no-member

        if object_hook is None:
            # To reuse the encoder from the JSONEncoder class we need to
            # create a new instance of the encoder with the same parameters
            # as the JSONEncoder class and only set the default method
            decoder = cls(
                date_format=date_format,
                datetime_format=datetime_format,
                use_undefined=use_undefined,
                instantiate_object=instantiate_object,
            )
            object_hook = decoder.custom_object_hook

        return _parser(result, object_hook=object_hook)

    if protocol == 'pickle':
        if settings.EVERYSK_SIGNING_KEY:
            data = unsign(data)

        return pickle.loads(data)

    raise ValueError(f"Unsupported serialize protocol '{protocol}'. Use 'json', 'orjson' or 'pickle'.")
