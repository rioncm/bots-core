"""
Environment reporting helpers for the extracted runtime core.
"""

from __future__ import annotations

import importlib.metadata
import os
import platform

from . import state
from .i18n import gettext as _


def _django_version():
    try:
        return importlib.metadata.version('django')
    except importlib.metadata.PackageNotFoundError:
        return None


def _database_info():
    if not state.settings:
        return []

    databases = getattr(state.settings, 'DATABASES', None)
    if not databases:
        return []

    connection_name = state.ini.get("settings", "django_db_connection", None)
    db_settings = databases.get(connection_name or "default")
    if not db_settings:
        return []

    infos = []
    if connection_name:
        infos.append(("django_db_connection", connection_name))
    infos.append(("DATABASE_ENGINE", db_settings["ENGINE"]))
    infos.append(("DATABASE_NAME", db_settings["NAME"]))
    if db_settings.get("USER"):
        infos.append(("DATABASE_USER", db_settings["USER"]))
    if db_settings.get("HOST"):
        infos.append(("DATABASE_HOST", db_settings["HOST"]))
    if db_settings.get("PORT"):
        infos.append(("DATABASE_PORT", db_settings["PORT"]))
    if db_settings.get("OPTIONS"):
        infos.append(("DATABASE_OPTIONS", db_settings["OPTIONS"]))
    return infos


def botsinfo():
    infos = [
        (_('webserver port'), state.ini.getint('webserver', 'port', 8080)),
        (_('platform'), platform.platform()),
        (_('machine'), platform.machine()),
        (_('python version'), platform.python_version()),
        (_('bots version'), state.version),
        (_('bots installation path'), state.ini.get('directories', 'botspath')),
        (_("botsenv path"), state.ini.get("directories", "botsenv")),
        (_('config path'), state.ini.get('directories', 'config')),
        (_('botssys path'), state.ini.get('directories', 'botssys')),
        (_('usersys path'), state.ini.get('directories', 'usersysabs')),
    ]

    django_version = _django_version()
    if django_version:
        infos.insert(4, (_('django version'), django_version))

    infos.extend(_database_info())
    return infos


def botsinfo_display():
    """:return str: Display bots infos"""
    txt = f"{os.linesep}---------- [Bots Environment] ----------{os.linesep}"
    txt += os.linesep.join([
        f"    {key:22}: {val}"
        for key, val in botsinfo() if key not in ['webserver port']])
    txt += os.linesep + "-" * 40
    return txt
