#!/usr/bin/env python
##############################################################################
#
# (c) 2025 The Trustees of Columbia University in the City of New York.
# All rights reserved.
#
# File coded by: Simon Billinge and members of the Billinge Group.
#
# See GitHub contributions for a more detailed list of contributors.
# https://github.com/diffpy/diffpy.cmi/graphs/contributors
#
# See LICENSE.rst for license information.
#
##############################################################################
"""Complex modeling infrastructure:
a modular framework for multi-modal modeling of scientific data."""

from importlib.resources import as_file, files


def get_package_dir():
    resource = files(__name__)
    return as_file(resource)


__all__ = [
    "__version__",
    "get_package_dir",
]

# package version
from diffpy.cmi.version import __version__  # noqa

assert __version__ or True

# End of file
