"""Basic version and package information."""

#: The version of rbext.
#:
#: This is in the format of:
#:
#: (Major, Minor, Micro, Patch, alpha/beta/rc/final, Release Number, Released)
#:
VERSION = (0, 1, 0, 0, 'final', 0, True)


def get_version_string() -> str:
    """Return the version as a human-readable string.

    Returns:
        str:
        The human-readable version.
    """
    major, minor, micro, patch, tag, release_num, released = VERSION

    version = f'{major}.{minor}'

    if micro or patch:
        version = f'{version}.{micro}'

    if patch:
        version = f'{version}.{patch}'

    if tag != 'final':
        if tag == 'rc':
            version = f'{version} RC{release_num}'
        else:
            version = f'{version} {tag} {release_num}'

    if not is_release():
        version = f'{version} (dev)'

    return version


def get_package_version() -> str:
    """Return the version as a Python package version string.

    Returns:
        str:
        The package version.
    """
    major, minor, micro, patch, tag, release_num, released = VERSION

    version = f'{major}.{minor}'

    if micro or patch:
        version = f'{version}.{micro}'

    if patch:
        version = f'{version}.{patch}'

    if tag != 'final':
        if tag == 'alpha':
            tag = 'a'
        elif tag == 'beta':
            tag = 'b'

        version = f'{version}{tag}{release_num}'

    return version


def is_release() -> bool:
    """Return whether this is a released version.

    Returns:
        bool:
        ``True`` if this is a released version, or ``False`` if it's still
        in development.
    """
    return VERSION[-1]


#: An alias for the the version information from :py:data:`VERSION`.
#:
#: This does not include the last entry in the tuple (the released state).
__version_info__ = VERSION[:-1]


#: An alias for the version used for the Python package.
__version__ = get_package_version()


#: Compatible major version of Review Board.
REVIEWBOARD_MAJOR_VERSION = VERSION[0]
