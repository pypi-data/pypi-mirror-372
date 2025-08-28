###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
import builtins

from ._version import get_versions

# This sets the Undefined as a global constant
# This works for all Python scripts and processes, but for some
# autocomplete tools like Pylance, Jedi etc... This does not work,
# so we need to search for "<tool> extends builtins" on Google
# to figure out how to solve the problem
try:
    builtins.Undefined
except AttributeError:
    from everysk.core.undefined import UndefinedType
    builtins.Undefined = UndefinedType()

    # Set UndefinedType to be blocked
    UndefinedType.block = True

version = get_versions()['version']
__version__ = version
del get_versions
