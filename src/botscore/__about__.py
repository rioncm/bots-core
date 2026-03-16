"""
botscore package metadata.
"""

from importlib import metadata

__all__ = [
    '__version__',
    '__version_info__',
    '__title__',
    '__summary__',
]

__title__ = 'botscore'
__summary__ = 'Framework-free translation runtime extraction for Bots'


def _resolve_version() -> str:
    for distribution_name in ('botscore', 'bots-ediint'):
        try:
            return metadata.version(distribution_name)
        except metadata.PackageNotFoundError:
            continue
    return '0+unknown'


__version__ = _resolve_version()
__version_info__ = __version__.split('.')
