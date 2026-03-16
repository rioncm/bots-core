"""
Configuration helpers for the extracted runtime core.
"""

from __future__ import annotations

import configparser

from .errors import BotsError


class BotsConfig(configparser.RawConfigParser):
    """ConfigParser with Bots-style default handling."""
    # pylint: disable=arguments-differ

    def get(self, section, option, default='', **kwargs):
        if self.has_option(section, option):
            result = super().get(section, option, **kwargs)
            return result or default
        if default == '':
            raise BotsError(f'No entry "{option}" in section "{section}" in "bots.ini"')
        return default

    def getint(self, section, option, default, **kwargs):
        if self.has_option(section, option):
            return configparser.RawConfigParser.getint(self, section, option, **kwargs)
        return default

    def getboolean(self, section, option, default, **kwargs):
        if self.has_option(section, option):
            return configparser.RawConfigParser.getboolean(self, section, option, **kwargs)
        return default
