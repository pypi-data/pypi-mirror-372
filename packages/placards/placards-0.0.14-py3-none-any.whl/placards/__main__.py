import os
import json
import glob
import tempfile
import logging
import asyncio
import argparse

from os.path import dirname, join as pathjoin

import aiohttp
from aiohttp.client_exceptions import ClientError
from pyppeteer import launch
from pyppeteer.errors import PageError

from placards.__version__ import __version__
from placards import config
from placards.errors import ConfigError
from placards.platform import (
    get_addr, run_command, run_x11vnc, file_path, dir_path, bin_path,
    get_hostname,
)


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())
STARTUP = [
    # Hide mouse cursor.
    'unclutter',

    # Disable screen blanking and screensaver.
    'xset s noblank',
    'xset s off',
    'xset -dpms',
]
REBOOT = 'reboot now'
PREFERENCES_PATH = 'Default/Preferences'
LOADING_HTML = pathjoin(dirname(__file__), 'html/index.html')


def getLogLevelNames():
    if callable(getattr(logging, 'getLevelNamesMapping', None)):
        return logging.getLevelNamesMapping().keys()

    return [
        logging.getLevelName(x)
        for x in range(1, 101)
        if not logging.getLevelName(x).startswith('Level')
    ]


async def chrome(chrome_bin, profile_dir, debug=False):
    "Launch Chrome browser and navigate to placards server."
    args = [
        '--start-maximized',
        '--start-fullscreen',
        '--no-default-browser-check',
        '--autoplay-policy=no-user-gesture-required',
        f'--user-agent="Placards Linux Client {__version__}"',
    ]
    if config.getbool('IGNORE_CERTIFICATE_ERRORS', False):
        args.append('--ignore-certificate-errors')
    if not debug:
        args.extend([
            '--noerrdialogs',
            '--disable-infobars',
            '--kiosk',
        ])
    browser = await launch(
        headless=False,
        args=args,
        ignoreDefaultArgs=["--enable-automation"],
        dumpio=debug,
        executablePath=chrome_bin,
        userDataDir=profile_dir,
        defaultViewport=None,
        autoClose=False,
    )
    page = (await browser.pages())[0]
    return browser, page


def edit_json_file(path, **kwargs):
    "Change keys in .json file and save."
    try:
        with open(path, 'r') as f:
            o = json.load(f)
        for key, value in kwargs.items():
            o[key] = value
        with tempfile.NamedTemporaryFile('wt',
                                         prefix=dirname(path),
                                         delete=False) as f:
            json.dump(o, f)
            os.remove(path)
            os.rename(f.name, path)

    except Exception:
        LOGGER.exception('Error modifying JSON file: %s', path)


def setup(profile_dir):
    "Set up directories, permission, environment."
    # Ensure profile directory exists.
    try:
        os.makedirs(profile_dir)

    except FileExistsError:
        pass

    # Run startup commands to prepare X.
    for command in STARTUP:
        LOGGER.debug('Running startup command', command)
        run_command(command)

    for fn in glob.glob('Singleton*', root_dir=profile_dir):
        try:
            os.remove(pathjoin(profile_dir, fn))

        except Exception:
            LOGGER.warning(
                'Could not delete Singleton file %s', fn, exc_info=True)

    # Clear away crash status from Chrome prefs.
    edit_json_file(
        pathjoin(profile_dir, PREFERENCES_PATH),
        exited_cleanly=True,
        exit_type='Normal',
    )


def message_handler(message):
    LOGGER.info('Received placards command: %s', message['command'])

    if message['command'] == 'reboot':
        run_command(REBOOT)

    elif message['command'] == 'vnc':
        try:
            port = run_x11vnc()

        except Exception:
            LOGGER.exception('Failure starting x11vnc')
            return

        return {'host': get_addr(), 'port': port}

    elif message['command'] == 'info':
        return {
            'hostname': get_hostname(),
            'addr': get_addr(),
            'version': __version__,
            'type': 'Linux',
        }


async def main():
    "Main entry point."
    debug = config.getbool('DEBUG', False)
    log_level_name = config.get(
        'LOG_LEVEL',
        'INFO' if not debug else 'DEBUG'
    ).upper()
    log_file_path = config.get('LOG_FILE', None)
    log_level = getattr(logging, log_level_name)
    loading_url = f'file://{LOADING_HTML}'

    root = logging.getLogger()
    root.addHandler(logging.StreamHandler())
    if log_file_path:
        root.addHandler(
            logging.RotatingFileHandler(
                log_file_path, maxBytes=(10 * (1024 ** 2)), backupCount=3))
    root.setLevel(log_level)

    LOGGER.debug('Loading web client...')

    try:
        url = config.SERVER_URL
        chrome_bin = config.CHROME_BIN_PATH
        profile_dir = config.PROFILE_DIR

    except ConfigError as e:
        LOGGER.error('You must configure %s in config.ini!', e.args[0])
        return

    setup(profile_dir)

    browser, page = await chrome(chrome_bin, profile_dir, debug)
    page.setDefaultNavigationTimeout(0)

    while True:
        try:
            async with aiohttp.ClientSession() as s:
                await s.head(
                    url,
                    ssl=not config.getbool('IGNORE_CERTIFICATE_ERRORS', False)
                )
            break

        except ClientError:
            await page.goto(loading_url)
            LOGGER.warning('Error preloading url: %s', url, exc_info=True)
            await asyncio.sleep(5.0)

    await asyncio.sleep(3.0)

    while True:
        try:
            # We need this page to load, so we will keep trying until it works.
            await page.goto(url, waitUntil='networkidle2')
            break

        except PageError:
            LOGGER.warning('Error loading url: %s', url)
            await asyncio.sleep(5.0)

    await page.exposeFunction('placardsServer', message_handler)
    LOGGER.info('placardsServer function exposed.')

    try:
        # Once the page is loaded, wait for it to close.
        while not page.isClosed():
            await asyncio.sleep(0.1)

    finally:
        await browser.close()


class EnvDefault(argparse.Action):
    def __init__(self, env_var, required=True, default=None, **kwargs):
        if env_var and env_var in os.environ:
            default = os.environ[env_var]
        if required and default:
            required = False
        super().__init__(default=default, required=required, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Placards Linux Client')
    parser.add_argument(
        '-d', '--debug', choices=['true', 'false'],
        action=EnvDefault, env_var='DEBUG', required=False,
    )
    parser.add_argument(
        '-i', '--ignore-certificate-errors',
        action=EnvDefault, env_var='IGNORE_CERTIFICATE_ERRORS', required=False)
    parser.add_argument('-l', '--log-file', type=file_path, required=False)
    parser.add_argument(
        '-v', '--log-level',
        choices=getLogLevelNames(),
        action=EnvDefault, env_var='LOG_LEVEL', required=False)
    parser.add_argument('-u', '--url', type=str, required=False)
    parser.add_argument(
        '-p', '--profile-dir',
        type=dir_path, action=EnvDefault, env_var='PROFILE_DIR',
        required=False,
    )
    parser.add_argument(
        '-c', '--chrome-bin-path',
        required=False, type=bin_path, action=EnvDefault,
        env_var='CHROME_BIN_PATH',
    )

    args = parser.parse_args()

    for arg in ('debug', 'log_file', 'log_level', 'url',
                'profile_dir', 'chrome_bin_path', 'ignore_certificate_errors'):
        if not getattr(args, arg):
            continue
        config.set(arg.upper(), getattr(args, arg))

    asyncio.run(main())
