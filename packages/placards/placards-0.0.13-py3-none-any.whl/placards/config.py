import os
import sys
import logging
import configparser

from os.path import expanduser, join as pathjoin
from types import ModuleType

from placards.errors import ConfigError


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

_NAME = 'config.ini'
_DIRS = [
    '~/.placards/', '/etc/placards/',
]
_SECTION = 'placards'
_SENTINAL = object()


def _to_bool(s):
    if isinstance(s, bool):
        return s
    return s.lower() in ['1', 'yes', 'on', 'true']


def _read_config(paths=None):
    if paths is None:
        paths = [
            expanduser(pathjoin(dir, _NAME)) for dir in _DIRS
        ]
    LOGGER.info('Looking for config in %s', ', '.join(paths))
    parser = configparser.ConfigParser()
    parser.read(paths)
    return parser


class _ConfigModule(ModuleType):
    _config = None

    def __getattribute__(self, name):
        if name.startswith('_'):
            raise AttributeError(name)

        try:
            return object.__getattribute__(self, name)

        except AttributeError:
            pass

        config = object.__getattribute__(self, '_config')
        if config is None:
            config_path = os.getenv('PLACARDS_CONFIG_PATH', None)
            config = _read_config(config_path)
            setattr(self, '_config', config)

        try:
            value = config.get(_SECTION, name)

        except configparser.NoOptionError:
            raise ConfigError(name)

        setattr(self, name, value)
        return value

    def get(self, name, default=_SENTINAL):
        try:
            return getattr(self, name)

        except ConfigError:
            if default is _SENTINAL:
                raise
            return default

    def set(self, name, value):
        setattr(self, name.upper(), value)

    def getint(self, name, default=_SENTINAL):
        return int(self.getfloat(name, default))

    def getfloat(self, name, default=_SENTINAL):
        return float(self.get(name, default))

    def getbool(self, name, default=_SENTINAL):
        return _to_bool(self.get(name, default))


sys.modules[__name__].__class__ = _ConfigModule
