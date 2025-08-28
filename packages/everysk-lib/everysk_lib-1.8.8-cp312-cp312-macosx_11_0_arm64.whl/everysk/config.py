###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from contextlib import AbstractContextManager
from contextvars import ContextVar
from copy import deepcopy
from importlib import import_module
from inspect import getmembers, isroutine, isclass
from os import getenv
from os.path import dirname, exists, sep
from pathlib import Path, PosixPath
from re import findall
from types import TracebackType, UnionType
from typing import Any

from everysk.core.object import BaseObject, MetaClass
from everysk.utils import bool_convert


# The root path of the everysk lib we need this to create the correct stub file
EVERYSK_ROOT = dirname(__file__)


###############################################################################
#   Private Functions Implementation
###############################################################################
def _get_context_value(name: str) -> Any:
    """
    If we are in a python context we return the value
    that is in the context setting.
    If the settings is not found we raise a KeyError.

    Args:
        name (str): The settings name.

    Raises:
        KeyError: If the name is not found.
    """
    context_settings = SettingsManager.settings.get()
    # We only care for the values that are explicit set in this settings
    if context_settings:
        return context_settings.__dict__.get(name, Undefined)

    return Undefined

def _get_env_value__(name: str) -> Any:
    """
    Get the value from the environment and clean it.

    Args:
        name (str): The var name to search.
    """
    env_value = getenv(name)

    # This is a check to always get the correct value
    # that we received from the environment
    # https://everysk.atlassian.net/browse/COD-907
    if env_value is not None:
        attributes = getattr(Settings, SettingsMetaClass._attr_name, {}) # pylint: disable=protected-access
        try:
            attr_type = attributes[name]
            try:
                # Our fields have the clean_value method
                env_value = attr_type.clean_value(env_value)

            except AttributeError:
                # For the other types we try to convert the
                # value to the specific type that was declared
                # For bool types we use a specific function
                if attr_type != bool:
                    env_value = attr_type(env_value)
                else:
                    env_value = bool_convert(env_value)

        except KeyError:
            pass
    else:
        # If env_value is None then the var was not set
        env_value = Undefined

    return env_value

def _is_valid_path(path: str) -> bool:
    """
    Function that checks if a path is valid to load the settings module.

    Args:
        path (str): The full path that need be checked.
    """
    result = True
    # Python installation normally happens on venvs that are in the project path
    if 'site-packages/' in path:
        result = False

    # Git files could have copies of python files
    elif '.git/' in path:
        result = False

    return result


###############################################################################
#   Public Functions Implementation
###############################################################################
def get_full_dotted_path_module(entry: PosixPath, root: str) -> str:
    """
    From the full path we need to generate the module that is valid for import.
    Changes '/var/app/src/everysk/settings.py' to 'everysk.settings'.

    Args:
        entry (PosixPath): The posix path object.
        root (str): The root path that will be removed.
    """
    # /var/app/src/everysk/settings.py
    module = str(entry)

    # everysk/settings.py
    module = module.replace(f'{root}{sep}', '')

    # everysk/settings
    module = module.replace('.py', '')

    # everysk.settings
    module = module.replace(sep, '.')

    return module

def get_all_modules() -> list:
    """
    We search inside EVERYSK_ROOT and PROJECT_ROOT for 'settings.py'
    files and convert this files into python modules.

    Returns:
        list: A list of Python modules

    Example:
        >>> all_modules = get_all_modules()
        >>> print(all_modules)
        ... ['module1', 'module2']
    """
    search_name = 'settings.py'
    modules = []
    if EVERYSK_ROOT and exists(EVERYSK_ROOT):
        # we need to remove the '/everysk' from the path to create the correct module path
        root = EVERYSK_ROOT.replace(f'{sep}everysk', '')
        for entry in Path(EVERYSK_ROOT).rglob(search_name):
            modules.append(get_full_dotted_path_module(entry=entry, root=root))

    project_root = getenv('PROJECT_ROOT')
    if project_root and exists(project_root):
        for entry in Path(project_root).rglob(search_name):
            # The rglob function does not have a way to remove some paths
            # so we need to manually exclude the ones that are not required
            if _is_valid_path(path=entry.as_posix()):
                modules.append(get_full_dotted_path_module(entry=entry, root=project_root))

    return modules

def get_all_attributes() -> list[tuple[str, Any, Any]]:
    """
    Get all attributes from the settings modules except ones that starts with '_'

    Example:
        Consider a settings module 'my_settings.py' containing the following attributes:

        ...
        MY_SETTING_1 = 42
        MY_SETTING_2 = 'Hello, World!'
        _MY_SETTING_3 = 'Foo Bar'
        ...

        Calling get_all_attributes() will return:

        [
            ('MY_SETTING_1', int, 42),
            ('MY_SETTING_2', str, 'Hello, World!')
        ]
    """
    result = []

    for module in get_all_modules():
        # Import the module
        module = import_module(module)

        for attr, value in getmembers(module, predicate=lambda x: not isroutine(x) and not isclass(x)):
            if not attr.startswith('_'):
                try:
                    attr_value = value.default
                    attr_type = value
                except AttributeError:
                    attr_value = value
                    # If this attribute already has an annotation on the module we use it
                    # otherwise we get the class of the value as the annotation
                    # https://everysk.atlassian.net/browse/COD-3833
                    attr_type = module.__annotations__.get(attr, type(value))

                result.append((attr, attr_type, attr_value))
    return result

def update_settings_attributes(obj: 'Settings'):
    """
    Updates the attributes of the Settings class in the config.pyi file.

    This function updates the attribute definitions of the Settings class based on the attributes retrieved from the `get_all_attributes` function.

    Example:
        >>> from everysk.config import update_settings_attributes
        >>> update_settings_attribute()
        ...
    """
    with open(f'{EVERYSK_ROOT}/config.pyi', 'w', encoding='utf-8') as stubs:
        # This fix the correct type of SettingsManager.settings
        stubs.write('from contextvars import ContextVar\n')

        # This fix the stub file for the RegexField
        stubs.write('from re import Pattern\n\n')

        # Now we have dict and BaseDict in the stub file too
        stubs.write('from everysk.core.object import BaseDict\n\n')

        # Write the SettingsManager class
        stubs.write('class SettingsManager:\n')
        stubs.write('    settings: ContextVar\n')
        stubs.write('    token: str\n\n')

        # Write the Settings class
        stubs.write('class Settings:\n')

        attributes = set()
        for attr_name, attr_type, attr_value in get_all_attributes():
            obj.__set_attribute__(attr_name, attr_type, attr_value)
            try:
                # If attr_type is a Everysk Field the real value will be in the attr_type attribute
                attr_type = attr_type.attr_type
            except AttributeError:
                pass

            # For Union types we need to get the real types inside __args__
            if not isinstance(attr_type, UnionType):
                attr_type = attr_type.__name__
            else:
                attr_type = ' | '.join([t.__name__ for t in attr_type.__args__])

            # We could have some duplicated attributes so we keep then in a set
            attributes.add(f'    {attr_name}: {attr_type}\n')

        # Then we write all attributes in the stub file
        stubs.writelines(sorted(attributes))
        # To autocomplete the init params
        stubs.write('    def __init__(self, singleton: bool = True, **kwargs) -> None: ...\n')
        # Fix for the autocomplete works if a context var is created
        stubs.write('    def __enter__(self) -> \'Settings\': ...\n')

        # This is needed to VS Code understand the instance
        stubs.write('\nsettings: Settings\n')


###############################################################################
#   SettingsManager Class Implementation
###############################################################################
class SettingsManager(AbstractContextManager):
    settings: ContextVar = ContextVar('everysk-settings', default=None)
    token: str = None

    def __init__(self, context_settings: 'Settings' = Undefined) -> None:
        if context_settings:
            # We make a copy to not change the original
            context_settings = deepcopy(context_settings)
        else:
            # We create a fresh one
            context_settings = Settings(singleton=False)

        # Store the value inside the context var
        self.token = self.settings.set(context_settings)

    def __exit__(self, __exc_type: type[BaseException] | None, __exc_value: BaseException | None, __traceback: TracebackType | None) -> bool | None:
        """
        https://docs.python.org/3/library/stdtypes.html#contextmanager.__exit__

        Returns:
            bool | None: If return is False any exception will be raised.
        """
        # Clear all settings config exiting the context
        self.settings.reset(self.token)

        # return False to raise any errors if they happened
        return False


###############################################################################
#   SettingsMetaClass Class Implementation
###############################################################################
class SettingsMetaClass(MetaClass):

    def __new__(mcs, name: str, bases: tuple, attrs: dict) -> type:
        """
        Method that create the class object.

        Args:
            mcs (_type_): This class.
            name (str): The name of the new class -> Settings.
            bases (tuple): Parent for the new class -> BaseObject.
            attrs (dict): A list of attributes tha the new class will have.
        """
        obj = super().__new__(mcs, name, bases, attrs)

        # This is executed only one time for every python process
        # before the initialization of the instance, we update the attributes list
        update_settings_attributes(obj)

        return obj


###############################################################################
#   Settings Class Implementation
###############################################################################
class Settings(BaseObject, metaclass=SettingsMetaClass):

    def __new__(cls, singleton: bool = True, **kwargs) -> 'Settings':
        """
        Changed to keep only one instance for the class.

        Args:
            singleton (bool): Used to keep the same instance. Defaults to True.
        """
        if singleton:
            try:
                return settings
            except NameError:
                pass

        return object.__new__(cls)

    def __init__(self, **kwargs) -> None:
        # remove the singleton keyword
        if 'singleton' in kwargs:
            kwargs.pop('singleton')

        super().__init__(**kwargs)

    def __deepcopy__(self, memo: dict = None) -> 'Settings':
        """
        A deep copy constructs a new compound object and then, recursively,
        inserts copies into it of the objects found in the original.
        This method is used when we call deepcopy(obj).

        Args:
            memo (dict, optional): A memory object to avoid copy twice. Defaults to None.
        """
        # We need to copy the __dict__
        obj = deepcopy(self.__dict__, memo)

        # We create a new obj
        obj = type(self)(singleton=False, **obj)
        return obj

    def __enter__(self) -> 'Settings':
        """
        https://docs.python.org/3/library/stdtypes.html#contextmanager.__enter__

        Returns:
            Settings: A copy of the settings object.
        """
        # We must use deepcopy to keep all values that are already set
        return deepcopy(settings)

    def __exit__(self, __exc_type: type[BaseException] | None, __exc_value: BaseException | None, __traceback: TracebackType | None) -> bool | None:
        """
        https://docs.python.org/3/library/stdtypes.html#contextmanager.__exit__
        This method is required even if it only returns False

        Returns:
            bool | None: If return is False any exception will be raised.
        """
        return False

    def __getattribute__(self, name: str) -> Any:
        """
        This method try to first get the value from the environment
        if this does not exists get from the class.

        Args:
            name (str): The setting name.
        """
        ## For performance and to avoid some errors because
        ## we are trying to get other things that does not
        ## are attributes of this class
        if name.startswith('__') or name == '_config':
            return super().__getattribute__(name)

        # First we try to get the value from the context
        value = _get_context_value(name)
        if value is Undefined:
            # Second we try to get the value from the instance
            value = self.__dict__.get(name, Undefined)
            if value is Undefined:
                # Third we try to get from the environment
                value = _get_env_value__(name)
                if value is Undefined:
                    # Fourth we try to get from the class that is the default value
                    value = super().__getattribute__(name)

        if isinstance(value, str):
            try:
                # If is a normal string nothing happen
                value = value.format()
            except KeyError:
                # Otherwise is a string in this format:
                # '{SOME_SETTING}-rest-string' so we need to change SOME_SETTING
                # for the real value that is a settings

                # We get all {*} that appears
                keys = findall(r'{(.*?)}', value)
                # Then we get the real value of each key
                kwargs = {key: getattr(self, key) for key in keys}
                # Then we try to format the real string
                value = value.format(**kwargs)

        return value

    def __setattr__(self, name: str, value: Any) -> None:
        """
        This method set the value of every attribute inside the Settings object,
        we use it to choose if we set on the normal object or in the context object.
        If the context_settings exists it sets the value inside the context_settings.

        Args:
            name (str): The name of the attribute.
            value (Any): The value that needs to be stored.
        """
        context_settings = SettingsManager.settings.get()
        # If context settings does not exist or it is a context_settings
        # that is trying to store the value for this setting we use the default behavior
        if not context_settings or context_settings == self:
            super().__setattr__(name, value)
        else:
            # Otherwise we call the set for context_settings
            setattr(context_settings, name, value)
            SettingsManager.settings.set(context_settings)


###############################################################################
#   Here we load all computed settings on one var
###############################################################################
settings: Settings = Settings()
