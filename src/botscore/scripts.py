"""
Userscript execution helpers for the extracted runtime core.
"""

from __future__ import annotations

from . import state
from .errors import (
    KillWholeFileException,
    ParsePassthroughException,
    ScriptError,
    txtexc,
)


def _gettext(text):
    return text


def runscript(module, modulefile, functioninscript, **argv):
    """
    Execute userscript. Functioninscript is supposed to be there; if not AttributeError is raised.
    Often is checked in advance if Functioninscript does exist.
    """
    if state.logger:
        state.logger.debug(
            'Run userscript "%(functioninscript)s" in "%(modulefile)s".',
            {'functioninscript': functioninscript, 'modulefile': modulefile},
        )
    functiontorun = getattr(module, functioninscript)
    try:
        if callable(functiontorun):
            return functiontorun(**argv)
        return functiontorun

    except (ParsePassthroughException, KillWholeFileException):
        raise

    except Exception as exc:
        txt = txtexc()
        _exception = ScriptError(
            _gettext('Userscript "%(modulefile)s": "%(txt)s".'),
            {'modulefile': modulefile, 'txt': txt},
        )
        raise _exception from exc


def tryrunscript(module, modulefile, functioninscript, **argv):
    if module and hasattr(module, functioninscript):
        runscript(module, modulefile, functioninscript, **argv)
        return True
    return False


def runscriptyield(module, modulefile, functioninscript, **argv):
    if state.logger:
        state.logger.debug(
            'Run userscript "%(functioninscript)s" in "%(modulefile)s".',
            {'functioninscript': functioninscript, 'modulefile': modulefile},
        )
    functiontorun = getattr(module, functioninscript)
    try:
        yield from functiontorun(**argv)
    except Exception as exc:
        txt = txtexc()
        _exception = ScriptError(
            _gettext('Script file "%(modulefile)s": "%(txt)s".'),
            {'modulefile': modulefile, 'txt': txt},
        )
        raise _exception from exc
