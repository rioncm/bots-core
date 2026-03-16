"""
Text and small data helpers for the extracted runtime core.
"""

from __future__ import annotations


def updateunlessset(updatedict, fromdict):
    """
    # !! TODO !! when is this valid?
    Note: prevents setting charset from grammar
    """
    updatedict.update(
        (key, value)
        for key, value in fromdict.items()
        if not updatedict.get(key)
    )


def rreplace(org, old, new='', count=1):
    """
    string handling:
    replace old with new in org, max count times.
    with default values: remove last occurence of old in org.
    """
    lijst = org.rsplit(old, count)
    return new.join(lijst)


def get_relevant_text_for_UnicodeError(exc):
    """see python doc for details of UnicodeError"""
    start = exc.start - 10 if exc.start >= 10 else 0
    return exc.object[start: exc.end + 35]
