"""
Runtime bootstrap helpers for the extracted translation core.
"""

from __future__ import annotations

import logging
import os
import sys

from . import state
from .codecs import initbotscharsets
from .config import BotsConfig
from .errors import PanicError
from .imports import botsbaseimport
from .net import settimeout
from .paths import dirshouldbethere

RUNTIME_DEFAULTS = {
    'settings': {
        'get_checklevel': '1',
        'globaltimeout': '10',
        'max_number_errors': '10',
        'debug': 'False',
        'readrecorddebug': 'False',
        'mappingdebug': 'False',
        'log_level': 'INFO',
        'log_console': 'False',
        'log_console_level': 'INFO',
        'log_file_level': 'INFO',
        'log_file_number': '5',
        'django_db_connection': '',
        'botsreplacechar': ' ',
        'log_when': 'report',
    },
    'webserver': {
        'environment': 'development',
    },
    'charsets': {},
    'dirmonitor': {},
}


def ensure_runtime_defaults(ini):
    """Ensure the runtime sections and baseline defaults exist."""
    if not ini.has_section('directories'):
        ini.add_section('directories')

    for section, values in RUNTIME_DEFAULTS.items():
        if not ini.has_section(section):
            ini.add_section(section)
        for key, value in values.items():
            if not ini.has_option(section, key):
                ini.set(section, key, value)


def load_config(config_path, *, botspath, configdir, botsenv):
    """Read bots.ini and populate runtime-critical directory metadata."""
    ini = BotsConfig()
    ensure_runtime_defaults(ini)
    ini.read(config_path)
    ensure_runtime_defaults(ini)

    configdirectory = os.path.abspath(os.path.dirname(config_path))
    ini.set('directories', 'botspath', os.path.abspath(botspath))
    ini.set('directories', 'config', configdirectory)
    ini.set('directories', 'config_org', configdir)
    ini.set('directories', 'botsenv', botsenv)
    return ini


def resolve_usersys_import(usersys):
    """Resolve the usersys package import path and absolute package directory."""
    usersys = os.path.normpath(usersys)
    try:
        importnameforusersys = usersys.replace(os.sep, '.')
        importedusersys = botsbaseimport(importnameforusersys)
    except ImportError:
        try:
            importnameforusersys = os.path.join('bots', usersys).replace(os.sep, '.')
            importedusersys = botsbaseimport(importnameforusersys)
        except ImportError as exc:
            if not os.path.exists(usersys):
                raise PanicError(
                    f'In initilisation: path to configuration does not exists: "{usersys}"'
                ) from exc
            addtopythonpath = os.path.abspath(os.path.dirname(usersys))
            importnameforusersys = os.path.basename(usersys)
            if addtopythonpath not in sys.path:
                sys.path.append(addtopythonpath)
            importedusersys = botsbaseimport(importnameforusersys)
    return importnameforusersys, importedusersys.__path__[0]


def configure_usersys(ini):
    """Resolve usersys and update the derived runtime directory settings."""
    usersys = os.path.normpath(ini.get('directories', 'usersys', 'usersys'))
    importnameforusersys, usersysabs = resolve_usersys_import(usersys)
    ini.set('directories', 'usersysabs', usersysabs)
    ini.set(
        'directories',
        'templatehtml',
        os.path.normpath(os.path.join(usersysabs, 'grammars', 'templatehtml', 'templates')),
    )
    return importnameforusersys


def configure_botssys(ini):
    """Normalize the botssys-derived runtime directories."""
    botssys = ini.get('directories', 'botssys', 'botssys')
    botsenv = ini.get('directories', 'botsenv')
    if os.path.isabs(botssys):
        botssys_abs = os.path.normpath(botssys)
    else:
        botssys_abs = os.path.normpath(os.path.join(botsenv, botssys))
    ini.set('directories', 'botssys_org', botssys)
    ini.set('directories', 'botssys', botssys_abs)
    ini.set('directories', 'data', os.path.join(botssys_abs, 'data'))
    ini.set('directories', 'logging', os.path.join(botssys_abs, 'logging'))
    ini.set('directories', 'users', os.path.join(botssys_abs, '.users'))
    ini.set('dirmonitor', 'trigger', os.path.join(botssys_abs, '.dirmonitor.trigger'))


def install_runtime(
    ini,
    *,
    configdir,
    usersys_import_path=None,
    logger=None,
    logmap=None,
    node_class=None,
    clear_not_import=False,
):
    """Install config/state for translation runtime use without Django setup."""
    state.ini = ini
    state.configdir = configdir
    state.usersysimportpath = usersys_import_path
    if clear_not_import:
        state.not_import.clear()
    if logger is not None:
        state.logger = logger
    if logmap is not None:
        state.logmap = logmap

    if ini.get('webserver', 'environment', 'development') != 'development':
        logging.raiseExceptions = 0

    dirshouldbethere(ini.get('directories', 'data'))
    dirshouldbethere(ini.get('directories', 'logging'))
    initbotscharsets()

    if node_class is not None:
        node_class.checklevel = ini.getint('settings', 'get_checklevel', 1)
    settimeout(ini.getint('settings', 'globaltimeout', 10))
