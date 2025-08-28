###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from typing import Any, Self


###############################################################################
#   UndefinedType Class Implementation
###############################################################################
#   Do not use this class, use the constant Undefined.
###############################################################################
class UndefinedType:
    """ The undefined type, to be used as value for attributes and params and be different from None."""
    default_error_message = 'This object is immutable.'
    default_parse_string = '__UNDEFINED_VALUE__'
    default_repr_string = '<Undefined value>'
    block = False

    def __init__(self) -> None:
        if self.block:
            raise NotImplementedError('Do not use this class, use the constant Undefined.')

    def __bool__(self):
        """ This object is always False """
        return False

    def __copy__(self) -> Self:
        """
        To keep consistence, this object will always be the same.
        """
        return self

    def __delattr__(self, __name: str) -> None:
        """ We could not delete attributes from this object. """
        raise AttributeError(self.default_error_message)

    def __deepcopy__(self, memo: dict = None) -> Self:
        """
        To keep consistence, this object will always be the same.
        """
        return self

    def __eq__(self, __value: object) -> bool:
        """
        For an object created from the UndefinedType class to be equal to another, the classes must be equal.
        """
        return isinstance(__value, type(self))

    def __getattr__(self, __name: str) -> Any:
        """ This object don't have attributes. """
        raise AttributeError(self.default_error_message)

    def __hash__(self) -> int:
        """ This must return an int that is used as hash for this object. """
        return id(self)

    def __repr__(self) -> str:
        """ Fixed to be the same every time. """
        return self.default_repr_string

    def __setattr__(self, __name: str, __value: Any) -> None:
        """ We can't set any attribute to this object. """
        if self.block:
            raise AttributeError(self.default_error_message)

    def __str__(self) -> str:
        """ Fixed to be the same every time. """
        return self.default_repr_string
