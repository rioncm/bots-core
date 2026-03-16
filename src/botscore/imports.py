"""
Dynamic import helpers for the extracted runtime core.
"""

from __future__ import annotations

import importlib
import os
import sys

from . import state
from .errors import BotsImportError, ScriptImportError


def _gettext(text):
    return text


def botsbaseimport(modulename):
    """
    Do a dynamic import.
    Errors/exceptions are handled in calling functions.
    """
    if sys.version_info[0] > 2:
        return importlib.import_module(modulename, 'bots')
    return importlib.import_module(modulename.encode(sys.getfilesystemencoding()), 'bots')


def botsimport(*args):
    """
    import modules from usersys.
    return: imported module, filename imported module;
    if not found or error in module: raise
    """
    usersys_import_path = state.usersysimportpath
    usersys_abs = ''
    if state.ini is not None:
        usersys_abs = state.ini.get('directories', 'usersysabs', '')

    if usersys_abs:
        modulefile = os.path.normpath(os.path.join(usersys_abs, *args))
    else:
        modulefile = os.path.normpath(os.path.join(*args))

    if not usersys_import_path:
        errs = [
            _gettext(
                'No import of module "%(modulefile)s": usersys imports are not configured.'
            ),
            {'modulefile': modulefile},
        ]
        if state.logger:
            state.logger.debug(*errs)
        raise BotsImportError(*errs)

    modulepath = '.'.join((usersys_import_path,) + args)

    if modulepath in state.not_import:
        errs = [_gettext('No import of module "%(modulefile)s".'), {'modulefile': modulefile}]
        if state.logger:
            state.logger.debug(*errs)
        raise BotsImportError(*errs)

    try:
        module = botsbaseimport(modulepath)

    except ImportError as exc:
        state.not_import.add(modulepath)
        errs = [
            _gettext('No import of module "%(modulefile)s": %(txt)s.'),
            {'modulefile': modulefile, 'txt': exc},
        ]
        if state.logger:
            state.logger.debug(*errs)
        _exception = BotsImportError(*errs)
        _exception.__cause__ = None
        raise _exception from exc

    except Exception as exc:
        errs = [
            _gettext('Error in import of module "%(modulefile)s":\n%(txt)s'),
            {'modulefile': modulefile, 'txt': exc},
        ]
        if state.logger:
            state.logger.debug(*errs)
        _exception = ScriptImportError(*errs)
        _exception.__cause__ = None
        raise _exception from exc

    if state.logger:
        state.logger.debug('Imported "%(modulefile)s".', {'modulefile': modulefile})
    return module, modulefile
