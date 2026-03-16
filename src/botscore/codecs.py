"""
Charset registration helpers for the extracted runtime core.
"""

from __future__ import annotations

import codecs
import encodings

from . import state
from .errors import BotsImportError
from .imports import botsimport


def _ini_get(section, option, default=" "):
    try:
        return state.ini.get(section, option, default)
    except TypeError:
        return state.ini.get(section, option, fallback=default)


def initbotscharsets():
    """Set up Bots-specific charset handling."""
    codecs.register(codec_search_function)
    state.botsreplacechar = str(_ini_get("settings", "botsreplacechar", " "))
    codecs.register_error('botsreplace', botsreplacechar_handler)
    for key, value in state.ini.items('charsets'):
        encodings.aliases.aliases[key] = value


def codec_search_function(encoding):
    """Try to import a usersys charset definition."""
    try:
        module, _filename = botsimport('charsets', encoding)
    except BotsImportError:
        return None
    if hasattr(module, 'getregentry'):
        return module.getregentry()
    return None


def botsreplacechar_handler(info):
    """
    Replace a character outside a charset by the configured fallback char.
    Useful for fixed records where record length should not change.
    """
    return (state.botsreplacechar, info.start + 1)
