###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext

import versioneer


# No-op build_ext to disable actual C compilation
class NoOpBuild(build_ext):
    def run(self):
        pass


setup(
    version=versioneer.get_version(),
    ext_modules=[Extension('dummy', sources=[])],  # just to trigger platform tag
    cmdclass={'build_ext': NoOpBuild},
)
