"""
Network helpers for the extracted runtime core.
"""

from __future__ import annotations

import socket


def settimeout(milliseconds):
    """set a time-out for TCP-IP connections"""
    socket.setdefaulttimeout(milliseconds)
