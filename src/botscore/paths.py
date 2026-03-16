"""
Filesystem path helpers for the extracted runtime core.
"""

from __future__ import annotations

import os

from . import state


def join(*paths):
    """
    Does more as join.....
     - join the paths (compare os.path.join)
     - if path is not absolute, interpretate this as relative from botsenv directory.
     - normalize
    """
    return os.path.normpath(os.path.join(state.ini.get("directories", "botsenv"), *paths))


def dirshouldbethere(path: str) -> bool:
    """
    Create directory if path doesn't exist and return True
    :return:
        - True if one or several directory was created
        - False if path already exist
    """
    if path and not os.path.exists(path):
        os.makedirs(path)
        return True
    return False


def abspath(soort, filename):
    """get absolute path for internal files; path is a section in bots.ini """
    directory = state.ini.get('directories', soort)
    return join(directory, filename)


def abspathdata(filename):
    """
    abspathdata if filename incl dir: return absolute path; else (only filename):

    :return:
        absolute path (datadir)
    """
    if '/' in filename:
        return join(filename)
    directory = state.ini.get('directories', 'data')
    datasubdir = filename[:-3]
    if not datasubdir:
        datasubdir = '0'
    return join(directory, datasubdir, filename)


def deldata(filename):
    """delete internal data file."""
    filename = abspathdata(filename)
    try:
        os.remove(filename)
    except Exception:
        pass
