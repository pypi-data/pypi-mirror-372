###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from copy import copy, deepcopy
from inspect import isroutine
from types import GenericAlias, UnionType
from typing import Any, Iterator, Self
from _collections_abc import dict_items, dict_keys, dict_values

from everysk.core.datetime import DateTime, Date
from everysk.core.exceptions import DefaultError, RequiredError, FieldValueError


CLASS_KEY: str = '__class_path__'
CONFIG_ATTRIBUTE_NAME: str = '_config'


###############################################################################
#   Private functions Implementation
###############################################################################
def __get_field_value__(obj: Any, attr: str, value: Any) -> Any:
    """
    Function that get the cleaned value for a Field and validate this value.

    Args:
        obj (Any): A class or a instance of BaseObject.
        attr (str): The attribute name.
        value (Any): The value that is assigned to this attribute.

    Raises:
        FieldValueError: If we find validation errors.
    """
    # Transforms the given value to Undefined if it matches the default_parse_string.
    value = _transform_to_undefined(value)

    # Get all attributes that the object has
    attributes = getattr(obj, MetaClass._attr_name) # pylint: disable=protected-access
    try:
        field = attributes[attr]
    except KeyError:
        return value

    # field can be the type itself or an instance of BaseField
    if isinstance(field, BaseField):
        try:
            value = field.get_cleaned_value(value)
        except Exception as error:
            # Add attribute name to error
            error.args = (f'{attr}: {str(error)}',)
            raise FieldValueError(error.args) from error

        field.validate(attr, value)
    else:
        _validate(attr, value, field)

    return value

def _transform_to_undefined(value: Any) -> Any:
    """
    Transforms the given value to Undefined if it matches the default parse string.

    Args:
        value (Any): The value to transform.

    Returns:
        Any: The transformed value.
    """
    if isinstance(value, str) and value == Undefined.default_parse_string:
        value = Undefined

    return value

def _required(attr_name: str, value: Any) -> None:
    """
    Checks if value is required, required values can't be: None, '', [], {}.

    Raises:
        RequiredError: When value is required and match with False conditions.
    """
    if value in (Undefined, None, '', (), [], {}):
        raise RequiredError(f'The {attr_name} attribute is required.')

def _validate(attr_name: str, value: Any, attr_type: type | UnionType) -> None: # pylint: disable=too-many-branches, too-many-return-statements
    """
    Validates that the given value is of the expected attribute type. The function supports special type checks for
    Date and DateTime types and handles general type validation for other types. It allows the value to pass through
    if it matches the expected type, is None, or is an instance of Undefined. The function uses custom checks for Date
    and DateTime to accommodate their unique validation requirements.

    Args:
        attr_name (str):
            The name of the attribute being validated. This is used for generating error messages.

        value (Any):
            The value to be validated against the expected type.

        attr_type (type):
            The expected type of the value. This can be a standard Python type, a custom type, or
            specific types like Date and DateTime which have dedicated validation logic.

    Raises:
        FieldValueError: When value is not of value_type.
    """
    # We always accept these 2 values
    if value is None or value is Undefined:
        return None

    if attr_type == Date:
        # If we are expecting a Date we don't need to check other things
        if Date.is_date(value):
            return None

    if attr_type == DateTime:
        # If we are expecting a DateTime we don't need to check other things
        if DateTime.is_datetime(value):
            return None

    # TypeError: typing.Any cannot be used with isinstance()
    if attr_type is Any:
        return None

    # https://everysk.atlassian.net/browse/COD-4286
    # If we use 'class'/callable as a annotation, the isinstance will fail
    # because attr_type will be a string/function so we need to discard it first
    if attr_type is callable:
        if callable(value):
            return None

    # If it is string, when we use classes as annotations we check if the name of the class is the same
    if isinstance(attr_type, str):
        if type(value).__name__ == attr_type:
            return None

    try:
        # Check if value is an instance of the expected type
        # If attr_type is a UnionType - int | float, the isinstance will work
        if isinstance(value, attr_type):
            return None
    except TypeError:
        pass

    ## Subscriptable types like List, Dict, Tuple, etc
    if isinstance(attr_type, GenericAlias):
        # We need to check if the value is a instance of the origin type
        if isinstance(value, attr_type.__origin__):
            # We not check the content of the list, dict, tuple, etc
            return None

    raise FieldValueError(f'Key {attr_name} must be {attr_type}.')


###############################################################################
#   BaseField Class Implementation
###############################################################################
class BaseField:
    """ Base class of all fields that will guarantee their type. """
    ## Public attributes
    attr_type: type | UnionType = None
    default: Any = None
    readonly: bool = False
    required: bool = False
    required_lazy: bool = False
    empty_is_none: bool = False

    def __init__(
        self,
        attr_type: type | UnionType = None,
        default: Any = None,
        readonly: bool = False,
        required: bool = False,
        required_lazy: bool = False,
        empty_is_none: bool = False,
        **kwargs
    ) -> None:
        """
        Use kwargs to set more attributes on the Field.

        Raises:
            DefaultError: For default values they can't be empty [] or {}.
            RequiredError: If field is readonly, then default value is required.
        """
        self.attr_type = attr_type
        if required and required_lazy:
            raise FieldValueError("Required and required_lazy can't be booth True.")

        self.required = required
        self.required_lazy = required_lazy

        if default is not None and not default and isinstance(default, (list, dict)):
            # For default values they can't be empty [] or {} - because this can cause
            # some issues with class attributes where these type can aggregate values.
            raise DefaultError('Default value cannot be a list or a dict.')

        if readonly and (default is None or default is Undefined):
            raise RequiredError('If field is readonly, then default value is required.')

        self.readonly = readonly

        # We use this flag to convert '' to None
        self.empty_is_none = empty_is_none

        # Other attributes will be assigned directly
        for key, value in kwargs.items():
            setattr(self, key, value)

        # For the last We need to store the cleaned value
        self.default = self.get_cleaned_value(default)

    def __repr__(self) -> str:
        """
        The `__repr__` method from `BaseField` returns the name of the
        instantiated class.

        Returns:
            str: The name of the class.
        """
        return self.__class__.__name__

    def __eq__(self, obj: object) -> bool:
        """
        One object will be equal to another one if all `__dict__`
        attributes are the same.

        Args:
            obj (object): The obj for comparison.
        """
        return self.__dict__ == obj.__dict__

    def transform_to_none(self, value: Any) -> Any:
        """
        Transforms value to None if needed.

        Args:
            value (Any): The value to be converted to `None`.

        Example:
            >>> field = BaseField(attr_type=str, empty_is_none=False)
            >>> field.transform_to_none('')
            ''

            >>> field = BaseField(attr_type=str, empty_is_none=True)
            >>> field.transform_to_none('')
            None
        """
        if self.empty_is_none and value == '':
            value = None

        return value

    def get_cleaned_value(self, value: Any) -> Any:
        """
        This function first converts the value to None if needed, then
        checks if the `value` is a callable. If it is, the function calls
        the `value` and stores its result by reassigning the `value` variable.
        Finally, the function calls the `clean_value` method.

        Args:
            value (Any): The cleaned value to be retrieved.

        Returns:
            Any: The cleaned value.
        """
        # We first verify if we need to transform the value to None
        value = self.transform_to_none(value)

        # Then we run the get_value method when value is a callable
        value = self.get_value(value)

        # Then we run the clean_value method
        value = self.clean_value(value)

        return value

    def get_value(self, value: Any) -> Any:
        """
        This function checks if the `value` is a callable
        By either returning the `value` or returning the
        result of the callable function.

        Must be implemented in child classes that need do some changes
        on received value before clean_value.

        Args:
            value (Any): The value to be possibly called.

        Returns:
            Any: The result of the callable function or the original value.
        """
        # If value is callable we call it
        if callable(value):
            value = value()

        return value

    def clean_value(self, value: Any) -> Any:
        """
        This method is always called when we assigned a value to some attribute.
        Must be implemented in child classes to change the behavior of a given field.
        Below we have an example that reimplements the `clean_value()`.

        Args:
            value (Any): The value to be cleaned.

        Usage:
            >>> from everysk.core.fields import BoolField
            >>> from everysk.core.object import BaseObject

            >>> class MyBoolField(BoolField):
            ...     def clean_value(self, value):
            ...         if value == 'test':
            ...             return True
            ...         return False

            >>> class MyClass(BaseObject):
            ...     f1 = MyBoolField()

            >>> a = MyClass()
            >>> a.f1 = True
            >>> a.f1
            False

            >>> a.f1 = 'test'
            >>> a.f1
            True
        """
        return value

    def validate(self, attr_name: str, value: Any, attr_type: type | UnionType = None) -> None:
        """
        Checks if value is required and if is of correct type.
        This method can be reimplemented in child classes to modify
        the behavior.

        Raises:
            RequiredError: If required and None is passed
            FieldValueError: If value type don't match with required type.

        Usage:
            >>> from everysk.core.fields import StrField
            >>> from everysk.core.object import BaseObject

            >>> class MyStrField(StrField):
            ...     def validate(self, attr_name, value):
            ...         if value == 'test':
            ...             raise ValueError("value argument cannot be 'test'")

            >>> class MyClass(BaseObject):
            ...     f1 = MyStrField()

            >>> a = MyClass()
            >>> a.f1 = 'test'
            ValueError: value argument cannot be 'test'
        """
        if attr_type is None:
            attr_type = self.attr_type

        if self.readonly:
            # This is necessary to be able to at least assign the default value to the field
            if value != self.default:
                raise FieldValueError(f"The field '{attr_name}' value cannot be changed.")

        if self.required and not self.required_lazy:
            _required(attr_name, value)

        _validate(attr_name, value, attr_type)

    def __getattr__(self, name: str) -> Any:
        """
        This method is used to handle pylint errors where the method/attribute does not exist.
        The problem is that we change the field in the MetaClass to the Field's default value,
        so StrField does not have the str methods but the result is a string.
        This method will only be executed if the method/attributes do not exist in the Field class.

        Args:
            name (str): The name of the method/attribute.
        """
        # https://pythonhint.com/post/2118347356810295/avoid-pylint-warning-e1101-instance-of-has-no-member-for-class-with-dynamic-attributes
        if not isinstance(self.attr_type, UnionType):
            return getattr(self.attr_type, name)

        # We try to get the attribute from the ones that are in the tuple
        for attr_type in self.attr_type.__args__:
            try:
                return getattr(attr_type, name)
            except AttributeError:
                pass

        # If no attribute was found we raise the error
        raise AttributeError(f"type object '{self.attr_type}' has no attribute '{name}'.")


###############################################################################
#   MetaClass Implementation
###############################################################################
def _silent(func: callable) -> callable:
    """
    Function that creates a silent decorator for the given function.
    This decorator will catch any exception raised by the function and store it.

    Args:
        func (callable): The function to be decorated.
    """
    def wrapper(self, *args, **kwargs):
        # pylint: disable=broad-exception-caught, protected-access
        silent = kwargs.pop('silent', self._silent)
        try:
            return func(self, *args, **kwargs)
        except Exception as error:
            if not silent:
                raise error
            if self._errors is None:
                self._errors = {}
            self._errors['init'] = deepcopy(error)

        return None

    return wrapper

class MetaClass(type):
    _attr_name: str = '__attributes__'
    _anno_name: str = '__annotations__'

    def __call__(cls, *args: tuple, **kwargs: dict) -> Self:
        """
        Method that creates a sequence of class call like:
            before_init
            init
            after_init
        If the BaseObject class implement one of these methods they will be executed.
        https://discuss.python.org/t/add-a-post-method-equivalent-to-the-new-method-but-called-after-init/5449/11
        """
        errors: dict[str: Exception | None] = {'before_init': None, 'init': None, 'after_init': None}
        # We get the silent from kwargs otherwise we get from the class
        silent = kwargs.get('silent', cls._silent)

        ## If the before init method is implemented we run it
        try:
            # If the method returns a dict we update kwargs
            dct = cls.__before_init__(**kwargs)
            if isinstance(dct, dict):
                kwargs = dct
        except Exception as error: # pylint: disable=broad-exception-caught
            if not silent:
                raise error
            errors['before_init'] = deepcopy(error)

        ## Here we create the object and initialize the silent for init must be inside the _silent function
        obj = super().__call__(*args, **kwargs)
        if obj._errors:
            errors['init'] = obj._errors['init']

        ## If the after init method is implemented we run it
        try:
            obj.__after_init__()
        except Exception as error: # pylint: disable=broad-exception-caught
            if not silent:
                raise error
            errors['after_init'] = deepcopy(error)

        # Store the errors
        if any(errors.values()):
            obj._errors = errors
            # Execute the handler for errors
            obj._init_error_handler(kwargs, errors)

        # Set the instance to be Frozen or not
        try:
            config = getattr(obj, CONFIG_ATTRIBUTE_NAME)
            obj._is_frozen = config.frozen # pylint: disable=attribute-defined-outside-init
        except AttributeError:
            pass

        return obj

    def __new__(mcs, name: str, bases: tuple, attrs: dict) -> Self:
        """
        This method is executed every time a BaseObject Class is created in the Python runtime.
        We changed this method to create the config and attributes properties and update the annotations.

        Example:
            >>> from everysk.core.object import BaseObject, CONFIG_ATTRIBUTE_NAME
            >>> class MyClass(BaseObject):
            ...     class Config:
            ...         value: int = 1

            >>> obj1 = MyClass()
            >>> obj2 = MyClass()
            >>> configC = getattr(MyClass, CONFIG_ATTRIBUTE_NAME)
            >>> config1 = getattr(obj1, CONFIG_ATTRIBUTE_NAME)
            >>> config2 = getattr(obj2, CONFIG_ATTRIBUTE_NAME)
            >>> configC == config1 == config2
            ... True

            >>> configC.value, config1.value, config2.value
            (1, 1, 1)

            >>> config2.value = 3
            >>> configC.value, config1.value, config2.value
            (3, 3, 3)

            >>> MyClass.Config
            ---------------------------------------------------------------------------
            AttributeError                            Traceback (most recent call last)
            ----> 1 MyClass.Config

            AttributeError: type object 'MyClass' has no attribute 'Config'

        Args:
            mcs (type): Represents this class.
            name (str): The name for the new class.
            bases (tuple): All inheritance classes.
            attrs (dict): All attributes that the new class has.

        Returns:
            type: Return the new class object.
        """
        # Creating the config property.
        if 'Config' in attrs:
            # If Config is in the class we just create it
            Config = attrs.pop('Config') # pylint: disable=invalid-name
            attrs[CONFIG_ATTRIBUTE_NAME] = Config()
        else:
            # If Config is not in the class we get the first one from the bases
            for base in bases:
                if hasattr(base, CONFIG_ATTRIBUTE_NAME):
                    config = getattr(base, CONFIG_ATTRIBUTE_NAME)
                    attrs[CONFIG_ATTRIBUTE_NAME] = deepcopy(config)
                    break

        # We need all attributes to validate the types later
        # So we need to get the parents attributes too
        attributes = {}
        for parent in bases:
            attributes.update(getattr(parent, mcs._attr_name, {}))

        # We could not update the info inside the original attrs dict because:
        # RuntimeError: dictionary changed size during iteration
        # So we remove the attributes that we need to update
        attributes.update(attrs.pop(mcs._attr_name, {}))
        annotations: dict = attrs.pop(mcs._anno_name, {})
        new_attrs = {}
        for attr_name, attr_value in attrs.items():
            if attr_name == '__init__':
                # To run all init in silent mode we need to decorate it
                new_attrs[attr_name] = _silent(attr_value)

            # We discard all python dunder attributes, all functions, all properties, Undefined and None values
            elif not attr_name.startswith('__') and \
               not isroutine(attr_value) and \
               not isinstance(attr_value, property) and \
               attr_value is not None and \
               attr_value is not Undefined:
                # For BaseFields we need to use the properties and set the correct value in the attribute
                if isinstance(attr_value, BaseField):
                    # We keep a copy of the value inside the __attributes__
                    attributes[attr_name] = attr_value

                    # We set the correct value to this attribute in the class
                    new_attrs[attr_name] = attr_value.default

                    # We create the annotation for this attribute
                    if attr_name not in annotations:
                        annotations[attr_name] = attr_value.attr_type
                else:
                    # For normal attributes we only store the class
                    attributes[attr_name] = type(attr_value)

                    # Now we update annotations for attributes that are not annotated
                    # Ex: var = 1
                    if attr_name not in annotations:
                        annotations[attr_name] = type(attr_value)

        # With both completed now we need to get the fields that are only annotations
        # class MyClass:
        #     var: str
        for key in annotations.keys() - attributes.keys():
            attributes[key] = annotations[key]
            # We set the default value to None to avoid break the code
            new_attrs[key] = None

        # We remove config from these to avoid validation/serialization problems
        if CONFIG_ATTRIBUTE_NAME in attributes:
            del attributes[CONFIG_ATTRIBUTE_NAME]

        if CONFIG_ATTRIBUTE_NAME in annotations:
            del annotations[CONFIG_ATTRIBUTE_NAME]

        # Readonly attributes need to go in the exclude list to generate the to_dict result correctly
        if CONFIG_ATTRIBUTE_NAME in attrs and hasattr(attrs[CONFIG_ATTRIBUTE_NAME], 'exclude_keys'):
            readonly_keys = {key for key, value in attributes.items() if getattr(value, 'readonly', False)}
            attrs[CONFIG_ATTRIBUTE_NAME].exclude_keys = attrs[CONFIG_ATTRIBUTE_NAME].exclude_keys.union(readonly_keys)

        # Then we update the attributes list for this new class
        attrs[mcs._attr_name] = attributes
        attrs[mcs._anno_name] = annotations
        attrs.update(new_attrs)

        return super().__new__(mcs, name, bases, attrs)

    def __setattr__(cls, __name: str, __value: Any) -> None:
        """
        Method that sets the values on fields of the class.

        Args:
            __name (str): The attribute name.
            __value (Any): The value that is set.
        """
        return super().__setattr__(__name, __get_field_value__(cls, __name, __value))


###############################################################################
#   BaseObject Class Implementation
###############################################################################
class _BaseObject(metaclass=MetaClass):
    """
    To ensure correct check for data keys
    uses https://docs.python.org/3/library/typing.html standards.

        >>> from utils.object import BaseObject
        >>> class MyObject(BaseObject):
        ...     var_int: int = None
        ...
        >>> obj = MyObject(var_int='a')
        Traceback (most recent call last):
        File "<stdin>", line 1, in <module>
        File "/var/app/utils/object.py", line 151, in __init__
            setattr(self, key, value)
        File "/var/app/utils/object.py", line 209, in __setattr__
            value = self.__get_clean_value__(__name, value)
        File "/var/app/utils/object.py", line 192, in __get_clean_value__
            _validate(attr, value, annotations[attr])
        File "/var/app/utils/object.py", line 56, in _validate
            raise DataTypeError(f'Key {attr_name} must be {attr_type}.')
        utils.exceptions.DataTypeError: Key var_int must be <class 'int'>.
    """
    ## Private attributes
    __slots__ = ('_need_validation',) # If we need to validate the data on setattr.
    _errors: dict = None # Keep the init errors.
    _is_frozen: bool = False # This will control if we can update data on this class.
    _silent: bool = False # If true an error that happen on init will be stored in self._error.

    def __new__(cls, *args, **kwargs) -> Self:
        obj = super().__new__(cls)

        # Initialize the _need_validation attribute always as True to validate all fields
        if not hasattr(obj, '_need_validation') or obj._need_validation is None:
            obj._need_validation = True

        return obj

    @classmethod
    def __before_init__(cls, **kwargs: dict) -> dict:
        """
        Method that runs before the __init__ method.
        If needed we must return the kwargs that will be passed to the init
        otherwise return None to not change the current behavior.
        """
        return kwargs

    def __init__(self, **kwargs: dict) -> None:
        # Validate all required fields
        attributes = self.__get_attributes__()
        for attr_name, field in attributes.items():
            if getattr(field, 'required', False):
                _required(attr_name=attr_name, value=kwargs.get(attr_name))

        # Set all kwargs on the object
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __after_init__(self) -> None:
        """
        Method that runs after the __init__ method.
        This method must return None.
        """
        pass

    def __check_frozen__(self) -> None:
        """
        Method that checks if this class is a Frozen object and raises attribute error.
        """
        if self._is_frozen:
            raise AttributeError(f'Class {self.get_full_doted_class_path()} is frozen and cannot be modified.')

    def __copy__(self) -> Self:
        """
        A shallow copy constructs a new compound object and then (to the extent possible)
        inserts references into it to the objects found in the original.
        If the object is Frozen the copy will not be.
        This method is used when we call copy(obj).
        """
        # We need to copy the __dict__
        obj = copy(self.__dict__)

        # We must not copy the config attribute because the copy could override the original in the class
        obj.pop(CONFIG_ATTRIBUTE_NAME, None)

        # We create a new obj
        obj = type(self)(**obj)
        return obj

    def __deepcopy__(self, memo: dict = None) -> Self:
        """
        A deep copy constructs a new compound object and then, recursively,
        inserts copies into it of the objects found in the original.
        This method is used when we call deepcopy(obj).

        Args:
            memo (dict, optional): A memory object to avoid copy twice. Defaults to None.
        """
        # We need to copy the __dict__
        obj = deepcopy(self.__dict__, memo)

        # We must not copy the config attribute because the copy could override the original in the class
        obj.pop(CONFIG_ATTRIBUTE_NAME, None)

        # We create a new obj
        obj = type(self)(**obj)
        return obj

    def __delattr__(self, __name: str) -> None:
        """
        Method that removes __name from the object.

        Args:
            __name (str): The name of the attribute that will be removed.

        Raises:
            AttributeError: If is frozen.
        """
        self.__check_frozen__()
        super().__delattr__(__name)

    def __get_attributes__(self) -> dict:
        """
        Get all attributes from this class.
        """
        return getattr(self, MetaClass._attr_name) # pylint: disable=protected-access

    def __get_clean_value__(self, attr: str, value: Any) -> Any:
        """
        Pass value to a clean function and checks if value match's the correct type.

        Raises:
            FieldValueError: If value and type don't match the correct type.
        """
        return __get_field_value__(self, attr, value)


    def _init_error_handler(self, kwargs: dict, errors: dict[str, Exception]) -> None:
        """
        This method is called at the end of the init process if the silent param is True.

        Args:
            errors (dict): A dict {'before_init': None | Exception, 'init': None | Exception, 'after_init': None | Exception}
        """
        pass

    def __setattr__(self, __name: str, __value: Any) -> None:
        """
        Method changed from BaseClass for check de integrity of data.
        This method is executed on setting attributes in the object.
        Ex: obj.attr = 1

        Raises:
            AttributeError: If is frozen.
        """
        self.__check_frozen__()

        if getattr(self, '_need_validation', True):
            __value = self.__get_clean_value__(__name, __value)

        super().__setattr__(__name, __value)

    @classmethod
    def __set_attribute__(cls, attr_name: str, attr_type: Any, attr_value: Any) -> None:
        """
        Method that updates the list of attributes/annotations for this class.
        Normally this is used to update a class after it was created.

        Args:
            attr_name (str): The name for the new attribute.
            attr_type (Any): The type for the new attribute.
            attr_value (Any): The value for the new attribute.
        """
        attributes = getattr(cls, MetaClass._attr_name, {}) # pylint: disable=protected-access
        annotations = getattr(cls, MetaClass._anno_name, {}) # pylint: disable=protected-access
        try:
            # For BaseFields
            annotations[attr_name] = attr_type.attr_type
        except AttributeError:
            # Normal types
            annotations[attr_name] = attr_type

        attributes[attr_name] = attr_type
        # After we set the attributes/annotations we set the value in the class
        setattr(cls, attr_name, attr_value)

    ## Public methods
    def get_full_doted_class_path(self) -> str:
        """
        Return full doted class path to be used on import functions.

        Example:
            'everysk.core.BaseObject'
        """
        return f'{self.__module__}.{self.__class__.__name__}'

    def replace(self, **changes) -> Self:
        """
        Creates a new object of the same type as self, replacing fields with values from changes.

        Args:
            **changes (dict): All named params that are passed to this method.

        Returns:
            Self: A copy of this object with the new values.

        Example:
            >>> from everysk.core.object import BaseObject
            >>> obj = BaseObject(attr=1)
            >>> obj.attr
            1
            >>> copy = obj.replace(attr=2)
            >>> copy.attr
            2
        """
        obj = deepcopy(self.__dict__)

        # We must not copy the config attribute because the copy could override the original in the class
        obj.pop(CONFIG_ATTRIBUTE_NAME, None)

        obj.update(changes)
        return type(self)(**obj)

    def validate_required_fields(self) -> None:
        """
        Try to validate all fields that are checked with required_lazy, because fields with
        required are always validate on the init.
        """
        attributes = self.__get_attributes__()
        for attr_name, field in attributes.items():
            if getattr(field, 'required_lazy', False):
                _required(attr_name=attr_name, value=getattr(self, attr_name, None))


###############################################################################
#   BaseObjectConfig Implementation
###############################################################################
class BaseObjectConfig(_BaseObject):
    exclude_keys: frozenset[str] = frozenset([])
    key_mapping: dict = None

    def __init__(self, **kwargs: dict) -> None:
        """ Use kwargs to set more attributes on the Config. """
        super().__init__(**kwargs)
        if self.key_mapping is None:
            self.key_mapping = {}


###############################################################################
#   BaseObject Class Implementation
###############################################################################
class BaseObject(_BaseObject):
    class Config(BaseObjectConfig):
        pass

    ## Private attributes
    _config: Config = None

    def __getstate__(self) -> dict:
        """
        This method is used by Pickle module to get the correct serialized data.
        https://docs.python.org/3.11/library/pickle.html#handling-stateful-objects
        """
        # This generates a dictionary with all attributes
        # We need to get the keys that are set in the instance and in the parents
        keys = self.__dict__.keys() | self.__get_attributes__().keys()

        # Then config key need to be removed and the exclude_keys list too
        config = getattr(self, CONFIG_ATTRIBUTE_NAME)
        keys = keys - {CONFIG_ATTRIBUTE_NAME} - set(config.exclude_keys)

        dct: dict = {key: getattr(self, key) for key in keys}

        # We set the _need_validation attribute to False because we already validated all data
        dct['_need_validation'] = False

        return dct

    def __setstate__(self, state: dict = None) -> None:
        """
        This method is used by Pickle module to set back the correct serialized data.
        We need to iterate over every key and set the value to the object.

        Args:
            state (dict): The result from the __getstate__ method used by Pickle.
        """
        if state:
            old_need_validation = self._need_validation
            # Set if we need validate every attribute
            self._need_validation = state.pop('_need_validation', True)
            for key, value in state.items():
                setattr(self, key, value)
            # Set the original value to validate the attributes
            self._need_validation = old_need_validation

    def to_native(self, add_class_path: str | None = None, recursion: bool = False) -> Any:
        """
        Converts the object to the specified Python type.

        Args:
            add_class_path (str | None, optional): The class path to add when converting the object. Defaults to None.
            recursion (bool, optional): Indicates whether to recursively convert nested objects. Defaults to False.

        Returns:
            object: The converted object.

        """
        return self.to_dict(add_class_path=add_class_path, recursion=recursion)

    def to_dict(self, add_class_path: bool = False, recursion: bool = False) -> dict:
        """
        This method is used to convert the object to a dictionary.
        If add_class_path is True, the full doted class path will be added to the dictionary.
        If recursion is True, the method will call the to_dict method of the child objects.

        Args:
            add_class_path (bool, optional): Flag to add the class path in the result. Defaults to False.
            recursion (bool, optional): Flag to transform the children too. Defaults to False.
        """
        dct: dict = {}
        # We need to get the keys that are set in the instance
        keys = self.__dict__.keys()
        if add_class_path:
            # If add_class_path is True we need to add all other keys that are in the class with the default value
            keys = keys | self.__get_attributes__().keys()

        def no_op(value: Any) -> Any:
            """ Function used to return the value in the getattr. """
            return value

        # Then config key need to be removed and the exclude_keys too
        config = getattr(self, CONFIG_ATTRIBUTE_NAME)
        keys = keys - {CONFIG_ATTRIBUTE_NAME} - set(config.exclude_keys)

        for key in keys:
            value = getattr(self, key)
            func = getattr(self, f'_process_{key}', no_op)
            key = config.key_mapping.get(key, key)
            result = func(value)
            if recursion and isinstance(result, BaseObject):
                result = result.to_dict(add_class_path=add_class_path, recursion=recursion)

            dct[key] = result

        if add_class_path:
            dct[CLASS_KEY] = self.get_full_doted_class_path()

        return dct


###############################################################################
#   BaseDictConfig Implementation
###############################################################################
class BaseDictConfig(BaseObjectConfig):
    keys_blacklist: frozenset[str] = frozenset([])


###############################################################################
#   BaseDict Class Implementation
###############################################################################
class BaseDict(BaseObject):
    """
    Extends BaseObject and also guarantees that BaseDict['key'] is equal to BaseDict.key

        >>> from utils.object import BaseDict
        >>> class MyDict(BaseDict):
        ...     var_int: int = None
        ...
        >>> obj = MyDict(var_int='test')
        Traceback (most recent call last):
        File "<stdin>", line 1, in <module>
        File "/var/app/utils/object.py", line 151, in __init__
            raise DataTypeError(f'Key {attr_name} must be {attr_type}.')
        File "/var/app/utils/object.py", line 279, in __setattr__
            if key.startswith('_'):
        File "/var/app/utils/object.py", line 209, in __setattr__
            DataTypeError: If value and type don't match the correct type.
        File "/var/app/utils/object.py", line 192, in __get_clean_value__
            # Create base annotations
        File "/var/app/utils/object.py", line 56, in _validate
            elif isinstance(value, attr_type):
        utils.exceptions.DataTypeError: Key var_int must be <class 'int'>.
        >>> obj = MyDict(var_int=10)
        >>> obj['var_int'] == obj.var_int
        True
    """
    class Config(BaseDictConfig):
        pass

    ## Private attributes
    __slots__ = ('__data__',)
    _config: Config = None

    ## Private Methods
    def __new__(cls, *args, **kwargs) -> Self:
        obj = super().__new__(cls, *args, **kwargs)
        # We need to create this here because __init__ could crash if we use self.attr
        # before call the super or if we use silent=True and work with the object later
        # Create the __data__ attribute if it does not exist
        if not hasattr(obj, '__data__'):
            obj.__data__ = {}

        return obj

    def __init__(self, **kwargs) -> None:
        # This is only for pylint stop complaining about not having __dict__
        if not hasattr(self, '__dict__'):
            self.__dict__ = {}

        # Add all kwargs to the object as key/attributes
        super().__init__(**kwargs)

        # We need to get all attributes from the parent classes too
        # to work like a dict and to have correct equality checks and
        # to represent the object as a dict
        attributes = self.__get_attributes__()
        for key in attributes.keys() - kwargs.keys():
            if self.is_valid_key(key=key):
                self[key] = self[key]

    def __contains__(self, key: str) -> bool:
        """
        Check if key is in self or in a parent.

        Args:
            key (str): The key name to search.
        """
        return key in self.__data__

    def __delattr__(self, name: str, caller: str = None) -> None:
        """
        Removes an atribute from self.

        Args:
            name (str): The attribute that will be removed.
            caller (str, optional): Used to avoid recursion when internally called. Defaults to None.

        Raises:
            AttributeError: If the attribute is not found.
        """
        # Remove attribute
        super().__delattr__(name)

        # Caller not None means this method was called from __delitem__
        # then we do not call the method again avoiding infinite loop
        if caller is None:
            try:
                # Some times the attribute will not exists
                self.__delitem__(name, caller='__delattr__')
            except KeyError:
                pass

    def __delitem__(self, key: Any, caller: str = None) -> None:
        """
        Removes an key from self.

        Args:
            key (Any): The key that will be removed.
            caller (str, optional): Used to avoid recursion when internally called. Defaults to None.

        Raises:
            KeyError: If the key is not found.
        """
        # Remove key
        self.__data__.__delitem__(key)

        # Caller not None means this method was called from __delattr__
        # then we do not call the method again avoiding infinite loop
        if caller is None:
            self.__delattr__(key, caller='__delitem__')

    def __eq__(self, other: Any) -> bool:
        """
        Check if two objects are the same.

        Args:
            other (Any): The other object to compare.
        """
        return isinstance(other, BaseDict) and self.__data__ == other.__data__

    def __getattr__(self, name: str) -> Any:
        """
        If the self does not have the attribute this method is called.
        We check if the __data__ does not have the attribute.

        Args:
            name (str): The name of the desired attribute.

        Raises:
            AttributeError: If name is not found.
        """
        if name != '__data__':
            try:
                return getattr(self.__data__, name)
            except AttributeError:
                pass

        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'.")

    def __getitem__(self, key: str) -> Any:
        """
        Get key from self or search on a parent.

        Args:
            key (str): The key name to search.

        Raises:
            KeyError: If the key does not exist.
        """
        if self.is_valid_key(key=key):
            try:
                return self.__data__.__getitem__(key)
            except KeyError:
                pass

            try:
                return getattr(self, key)
            except AttributeError:
                pass

        raise KeyError(key) # pylint: disable=raise-missing-from

    def __ior__(self, other: Any) -> Any:
        """
        This method performs an in-place merge of two objects using the `|=` operator.
        If `other` is an instance of the same class, it merges the attributes of `other` into the `self` class.
        Otherwise, it tries to merge the `other` dictionary into the `self` class.

        Args:
            other (Any): The other object to merge.

        Returns:
            Any: The instance of the class with the merged attributes.
        """
        if isinstance(other, type(self)):
            self.__dict__ |= other.__dict__

        else:
            self.__dict__ |= other

        return self

    def __iter__(self) -> Iterator:
        """
        Iterate over the object keys.
        This method is used when we call a for over the instance:

        Example:
            >>> for key in BaseDict():
        """
        return iter(self.__data__)

    def __len__(self) -> int:
        """
        Get the length of the dictionary.

        Returns:
            int: The length of the dictionary.
        """
        return len(self.__data__)

    def __ne__(self, other: Any) -> bool:
        """
        Check if two objects are different.

        Args:
            other (Any): The other object to compare.
        """
        return not self.__eq__(other)

    def __or__(self, other: Any) -> Any:
        """
        This method is used to merge two objects using the `|` operator.
        It merges both objects using the `self.__dict__` method if `other` is an instance of the same class.
        Otherwise, if `other` is a dictionary, it merges `self.__dict__` with the `other` dictionary.

        Args:
            other (Any): The other object to merge.

        Returns:
            NotImplemented: If `other` is not an instance of the same class or an instance of a dictionary.
        """
        if isinstance(other, type(self)):
            return type(self)(**(self.__dict__ | other.__dict__))

        if isinstance(other, dict):
            return type(self)(**(self.__dict__ | other))

        # don't attempt to compare against unrelated types
        return NotImplemented

    def __repr__(self) -> str:
        """
        This method returns the representation of the object in a string format.

        Returns:
            str: The string representation of the object.
        """
        return self.__data__.__repr__()

    def __ror__(self, other: Any) -> Any:
        """
        This method is used to merge two objects using the `|` operator, with the current object being on the right-hand side.
        It merges the current object with `other` using the `__dict__` method if `other` is an instance of the same class.
        If `other` is a dictionary, it merges the `other` dictionary with `self.__dict__`.

        Args:
            other (Any): The other object to merge.

        Returns:
            NotImplemented: if `other` is not an instance of the same class or an instance of a dictionary.
        """
        if isinstance(other, type(self)):
            return type(self)(**(other.__dict__ | self.__dict__))

        if isinstance(other, dict):
            return type(self)(**(other | self.__dict__))

        # don't attempt to compare against unrelated types
        return NotImplemented

    def __setattr__(self, name: str, value: Any, caller: str = None) -> None:
        """
        Method changed from BaseClass for guarantee de integrity of data attributes.
        This method is executed on setting attributes in the object.
        Ex: obj.attr = 1

        Raises:
            AttributeError: If is frozen.
        """
        super().__setattr__(name, value)
        # Because self.__get_clean_value__ can change the value we need to pick it from self
        new_value = getattr(self, name)

        # When value is associated:
        # directly on the key Ex dict['key'] = value then caller will be __setitem__
        # directly on attribute Ex dict.key = value then caller will be None
        # Don't do that to private attributes
        if caller is None and self.is_valid_key(key=name):
            # For integrity guarantee writes the value to the dictionary key as well.
            self.__setitem__(name, new_value, caller='__setattr__')

    def __setitem__(self, key: str, item: Any, caller: str = None) -> None:
        """
        Method changed from BaseClass for guarantee de integrity of data keys.
        This method is executed on setting items in the dictionary.
        Ex: d = dict(key=1) or d['key'] = 1

        Raises:
            AttributeError: If is frozen.
        """
        if key.startswith('_'):
            raise KeyError("Keys can't start with '_'.")
        config = getattr(self, CONFIG_ATTRIBUTE_NAME)
        if key in config.keys_blacklist:
            raise KeyError(f'The key cannot be called "{key}".')

        # When value is associated:
        # directly on the key Ex dict['key'] = value then caller will be None
        # directly on attribute Ex dict.key = value then caller will be __setattr__
        if caller is None:
            # For integrity guarantee writes the value to the attribute as well.
            self.__setattr__(key, item, caller='__setitem__')

            # The setattr can "clean" the value them we need to catch it again
            item = getattr(self, key)

        # If key is a property we do not set on dict
        if not isinstance(getattr(type(self), key, None), property):
            self.__data__.__setitem__(key, item)

    def __setstate__(self, state: dict = None) -> None:
        """
        This method is used by Pickle module to set back the correct serialized data.
        We need to iterate over every key and set the value to the object.

        Args:
            state (dict): The result from the __getstate__ method used by Pickle.
        """
        # NOTE: coverage not passing here since `self` will always have __data__ attribute
        # For some old Pickle objects the data attribute will not exists so we need to create it
        if not hasattr(self, '__data__'):
            self.__data__ = {} # pylint: disable=attribute-defined-outside-init

        return super().__setstate__(state)


    ## Public Methods
    def clear(self) -> None:
        """
        This method clears the dictionary.

        Raises:
            AttributeError: If is frozen.
        """
        self.__check_frozen__()
        # Because we integrate key/attributes we need to remove booth
        # The original clear only remove keys
        # We need to convert keys to a list, because the original is a iterator
        for key in list(self.keys()):
            del self[key]

    def copy(self) -> dict:
        """
        Generate a copy for this object, we need to use deepcopy because
        this object could have some keys/attributes and they need to be on the copy.
        If the object is Frozen, the copy will not be.
        """
        return deepcopy(self)

    def fromkeys(self, keys: list, default: Any = None) -> dict:
        """
        Create a new object with the keys, if key does not exists add one with default value.
        If the object is Frozen, the copy will not be.

        Args:
            keys (list): The list with the keys for the new object.
            default (Any, optional): The default value if the key does not exists. Defaults to None.
        """
        # Create a new key list with all keys and use a set to avoid duplicates
        keys_aux = set(keys)
        keys_aux.update(self.keys())

        dct = self.copy()
        for key in keys_aux:
            if key in keys:
                dct[key] = dct.get(key, default)
            else:
                del dct[key]

        return dct

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get the value for the key, if key does not exists return default.

        Args:
            key (str): The key to get the value.
            default (Any, optional): The default value if the key does not exists. Defaults to None.

        Returns:
            Any: The value for the key or the default value.
        """
        return self.__data__.get(key, default)

    def is_valid_key(self, key: str) -> bool:
        """
        This method checks if the key is valid.
        Valid keys are the ones that not starts with '_' and
        are not in the config.keys_blacklist.

        Args:
            key (str): The key that needs to be checked.

        Returns:
            bool: True if the key is valid, False otherwise.
        """
        config = getattr(self, CONFIG_ATTRIBUTE_NAME)
        return not key.startswith('_') and key not in config.keys_blacklist

    def items(self) -> dict_items:
        """
        Return a new view of the dictionary's items ((key, value) pairs).
        """
        return self.__data__.items()

    def keys(self) -> dict_keys:
        """
        Return a new view of the dictionary's keys.
        """
        return self.__data__.keys()

    def pop(self, *args) -> Any:
        """
        Remove specified key and return the corresponding value.
        If the key is not found return the default otherwise raise a KeyError.

        Args:
            key (str): The key that will be removed.
            default (Any, optional): The default value if key is not found.

        Raises:
            AttributeError: If is frozen.
            KeyError: If the default is not passed and key is not found.
        """
        self.__check_frozen__()
        ret = self.__data__.pop(*args)

        try:
            # Some times the attribute will not exists
            self.__delattr__(args[0]) # pylint: disable=unnecessary-dunder-call
        except AttributeError:
            pass

        return ret

    def popitem(self) -> tuple:
        """
        Remove and return a (key, value) pair as a 2-tuple.
        Pairs are returned in LIFO (last-in, first-out) order.

        Raises:
            AttributeError: If is frozen.
            KeyError: If the dict is empty.
        """
        self.__check_frozen__()
        return self.__data__.popitem()

    def update(self, *args, **kwargs) -> None:
        """
        Update self with the key/value pairs that are passed.
        We check every value to see if it is valid.

        Example:

            >>> dct = BaseDict()
            >>> dct.update({'a': 1})
            >>> dct
            {'a': 1}
            >>> dct.update([('b', 2)])
            >>> dct
            {'a': 1, 'b': 2}

        Raises:
            AttributeError: If is frozen.
        """
        self.__check_frozen__()
        dct = dict(*args, **kwargs)
        for key, value in dct.items():
            if self.is_valid_key(key=key):
                self[key] = value
            else:
                raise KeyError(f'The key cannot be called "{key}".')

    def values(self) -> dict_values:
        """
        Return a new view of the dictionary's values.
        """
        return self.__data__.values()
