"""Tools for building Review Board extensions.

This is the primary module for rbext. It contains useful forwarding imports for
the project.
"""

from rbext._version import (VERSION,
                            __version__,
                            __version_info__,
                            get_package_version,
                            get_version_string,
                            is_release)


_all__ = [
    'VERSION',
    '__version__',
    '__version_info__',
    'get_package_version',
    'get_version_string',
    'is_release',
]
