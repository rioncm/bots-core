"""
Minimal translation helpers for the extracted runtime core.
"""

from __future__ import annotations


def gettext(text):
    """Use Django translations when available, otherwise return the original text."""
    try:
        # pylint: disable=import-outside-toplevel
        from django.utils.translation import gettext as django_gettext
    except Exception:
        return text

    try:
        return django_gettext(text)
    except Exception:
        return text
