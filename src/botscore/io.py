"""
File IO helpers for the extracted runtime core.
"""

from __future__ import annotations

import codecs
import os
import pickle

from .paths import abspathdata, dirshouldbethere


def _resolve_abspathdata(filename, resolve_abspathdata=None):
    if resolve_abspathdata is None:
        resolve_abspathdata = abspathdata
    return resolve_abspathdata(filename)


def opendata(filename, mode, charset=None, errors="strict", resolve_abspathdata=None):
    """open internal data file as unicode."""
    filename = _resolve_abspathdata(filename, resolve_abspathdata)
    if 'w' in mode:
        dirshouldbethere(os.path.dirname(filename))
    return codecs.open(filename, mode, charset, errors)


def readdata(filename, charset=None, errors="strict", resolve_abspathdata=None):
    """read internal data file in memory as unicode."""
    with opendata(filename, "r", charset, errors, resolve_abspathdata=resolve_abspathdata) as filehandler:
        return filehandler.read()


def opendata_bin(filename, mode="rb", resolve_abspathdata=None):
    """open internal data file as binary."""
    filename = _resolve_abspathdata(filename, resolve_abspathdata)
    if 'w' in mode:
        dirshouldbethere(os.path.dirname(filename))
    return open(filename, mode=mode)


def readdata_bin(filename, resolve_abspathdata=None):
    """read internal data file in memory as binary."""
    filehandler = opendata_bin(filename, mode='rb', resolve_abspathdata=resolve_abspathdata)
    content = filehandler.read()
    filehandler.close()
    return content


def readdata_pickled(filename, resolve_abspathdata=None):
    """pickle is a binary/byte stream"""
    filehandler = opendata_bin(filename, mode='rb', resolve_abspathdata=resolve_abspathdata)
    content = pickle.load(filehandler)
    filehandler.close()
    return content


def writedata_pickled(filename, content, resolve_abspathdata=None):
    """pickle is a binary/byte stream"""
    filehandler = opendata_bin(filename, mode='wb', resolve_abspathdata=resolve_abspathdata)
    pickle.dump(content, filehandler)
    filehandler.close()
