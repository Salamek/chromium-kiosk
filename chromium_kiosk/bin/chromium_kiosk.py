#!/usr/bin/env python3
"""Main entry-point into the 'Chromium Kiosk' application.

This is Chromium Kiosk.

License: GPL-3.0
Website: https://github.com/Salamek/chromium-kiosk

Command details:
    run                 Run the application.
    post_install        Post install hook.
Usage:
    chromium-kiosk run [-l DIR] [--config_prod]
    chromium-kiosk post_install [--config_prod]
    chromium-kiosk watch_config [--config_prod]
    chromium-kiosk system_info [--config_prod]
    chromium-kiosk (-h | --help)

Options:
    --config_prod               Load the production configuration instead of dev
    -l DIR --log_dir=DIR        Directory to log into
"""

import hashlib
import logging
import logging.handlers
import os
import pwd
import grp
import signal
import sys
import shutil
import asyncio
import json
import websockets
from functools import wraps
from importlib import import_module
from chromium_kiosk.Chromium import Chromium
from chromium_kiosk.Qiosk import Qiosk
from chromium_kiosk.enum.RotationEnum import RotationEnum
from chromium_kiosk.tools import create_user, \
    inject_parameters_to_url, \
    set_user_groups, \
    rotate_screen, \
    rotate_display, \
    rotate_touchscreen, \
    generate_xscreensaver_config, \
    detect_display, \
    detect_touchscreen_device_name, \
    detect_primary_screen, \
    get_screen_rotation, \
    get_touchscreen_rotation, \
    find_binary
import chromium_kiosk as app_root

import yaml
from docopt import docopt

OPTIONS = docopt(__doc__)
APP_ROOT_FOLDER = os.path.abspath(os.path.dirname(app_root.__file__))


def resolve_rotation_config(options):

    # Rotation options are set separately, use them
    if options.TOUCHSCREEN_ROTATION and options.SCREEN_ROTATION:
        rotate_screen(RotationEnum(options.SCREEN_ROTATION))
        rotate_touchscreen(RotationEnum(options.TOUCHSCREEN_ROTATION))
    elif not options.TOUCHSCREEN_ROTATION and options.SCREEN_ROTATION:
        rotate_screen(RotationEnum(options.SCREEN_ROTATION))
        rotate_touchscreen(RotationEnum.NORMAL)
    elif options.TOUCHSCREEN_ROTATION and not options.SCREEN_ROTATION:
        rotate_screen(RotationEnum.NORMAL)
        rotate_touchscreen(RotationEnum(options.TOUCHSCREEN_ROTATION))
    elif options.DISPLAY_ROTATION:
        rotate_display(RotationEnum(options.DISPLAY_ROTATION))
    else:
        # just fallback to normal
        rotate_display(RotationEnum.NORMAL)


class CustomFormatter(logging.Formatter):
    LEVEL_MAP = {logging.FATAL: 'F', logging.ERROR: 'E', logging.WARN: 'W', logging.INFO: 'I', logging.DEBUG: 'D'}

    def format(self, record):
        record.levelletter = self.LEVEL_MAP[record.levelno]
        return super(CustomFormatter, self).format(record)


def setup_logging(name: str=None, level: int=logging.DEBUG) -> None:
    """Setup Google-Style logging for the entire application.

    At first I hated this but I had to use it for work, and now I prefer it. Who knew?
    From: https://github.com/twitter/commons/blob/master/src/python/twitter/common/log/formatters/glog.py

    Always logs DEBUG statements somewhere.

    Positional arguments:
    name -- Append this string to the log file filename.
    """
    log_to_disk = False
    if OPTIONS['--log_dir']:
        if not os.path.isdir(OPTIONS['--log_dir']):
            print('ERROR: Directory {} does not exist.'.format(OPTIONS['--log_dir']))
            sys.exit(1)
        if not os.access(OPTIONS['--log_dir'], os.W_OK):
            print('ERROR: No permissions to write to directory {}.'.format(OPTIONS['--log_dir']))
            sys.exit(1)
        log_to_disk = True

    fmt = '%(levelletter)s%(asctime)s.%(msecs).03d %(process)d %(filename)s:%(lineno)d] %(message)s'
    datefmt = '%m%d %H:%M:%S'
    formatter = CustomFormatter(fmt, datefmt)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.ERROR if log_to_disk else logging.DEBUG)
    console_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(console_handler)

    if log_to_disk:
        file_name = os.path.join(OPTIONS['--log_dir'], 'chromium_kiosk_{}.log'.format(name))
        file_handler = logging.handlers.TimedRotatingFileHandler(file_name, when='d', backupCount=7)
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)


def get_config(config_class_string: str, yaml_files=None):
    """Load the Flask config from a class.
    Positional arguments:
    config_class_string -- string representation of a configuration class that will be loaded (e.g.
        'chromium_kiosk.config.Production').
    yaml_files -- List of YAML files to load. This is for testing, leave None in dev/production.
    Returns:
    A class object to be fed into app.config.from_object().
    """
    config_module, config_class = config_class_string.rsplit('.', 1)
    config_obj = getattr(import_module(config_module), config_class)

    # Expand some options.
    db_fmt = 'chromium_kiosk.models.{}'
    if getattr(config_obj, 'DB_MODELS_IMPORTS', False):
        config_obj.DB_MODELS_IMPORTS = [db_fmt.format(m) for m in config_obj.DB_MODELS_IMPORTS]

    # Load additional configuration settings.
    yaml_files = yaml_files or [f for f in [
        os.path.join('/', 'etc', 'chromium-kiosk', 'config.yml'),
        # Compability with old proprietary version
        os.path.join('/', 'etc', 'granad-kiosk', 'config.yml'),
        os.path.abspath(os.path.join(APP_ROOT_FOLDER, '..', 'config.yml')),
        os.path.join(APP_ROOT_FOLDER, 'config.yml'),
    ] if os.path.exists(f)]
    additional_dict = dict()
    for y in yaml_files:
        with open(y) as f:
            config_content = f.read()
            try:
                loaded_data = yaml.load(config_content, Loader=yaml.FullLoader)
            except AttributeError:
                # Handle older versions of yaml library
                loaded_data = yaml.load(config_content)
            if isinstance(loaded_data, dict):
                additional_dict.update(loaded_data)
            else:
                raise Exception('Failed to parse configuration {}'.format(y))

    # Merge the rest into the Flask app config.
    for key, value in additional_dict.items():
        setattr(config_obj, key, value)

    return config_obj


def parse_config():
    """Parses command line options for Flask.

    Returns:
    Config instance to pass into create_app().
    """
    # Figure out which class will be imported.
    if OPTIONS['--config_prod']:
        config_class_string = 'chromium_kiosk.config.Production'
    else:
        config_class_string = 'chromium_kiosk.config.Config'
    config_obj = get_config(config_class_string)

    return config_obj


def command(func):
    """Decorator that registers the chosen command/function.

    If a function is decorated with @command but that function name is not a valid "command" according to the docstring,
    a KeyError will be raised, since that's a bug in this script.

    If a user doesn't specify a valid command in their command line arguments, the above docopt(__doc__) line will print
    a short summary and call sys.exit() and stop up there.

    If a user specifies a valid command, but for some reason the developer did not register it, an AttributeError will
    raise, since it is a bug in this script.

    Finally, if a user specifies a valid command and it is registered with @command below, then that command is "chosen"
    by this decorator function, and set as the attribute `chosen`. It is then executed below in
    `if __name__ == '__main__':`.

    Doing this instead of using Flask-Script.

    Positional arguments:
    func -- the function to decorate
    """

    @wraps(func)
    def wrapped():
        return func()

    # Register chosen function.
    if func.__name__ not in OPTIONS:
        raise KeyError('Cannot register {}, not mentioned in docstring/docopt.'.format(func.__name__))
    if OPTIONS[func.__name__]:
        command.chosen = func

    return wrapped


@command
def run():
    config = parse_config()
    setup_logging('kiosk', logging.DEBUG if config.DEBUG else logging.WARNING)

    # Rotate screen by config value
    resolve_rotation_config(config)

    # detect what browser is installed to deduce what browser we will be using, qiosk has priority
    found_qiosk = find_binary(['qiosk'])
    if found_qiosk:
        selected_browser = Qiosk()
    else:
        # Fallback to chromium
        data_dir = os.getenv("DATADIR", "/usr/share")
        extension_path = os.path.join(data_dir, 'chromium-kiosk/chromium-kiosk-extension')
        selected_browser = Chromium(load_extension_path=extension_path if os.path.isdir(extension_path) else None)

    selected_browser.set_config(config)
    selected_browser.run()


@command
def watch_config():
    async def config_watcher(websocket, path):
        last_sum = None
        while True:
            try:
                config = parse_config()
                user_home = os.path.join('/', 'home', config.USER)

                client_options = {
                    'homePage': config.HOME_PAGE,
                    'idleTime': config.IDLE_TIME,
                    'displayRotation': config.DISPLAY_ROTATION,
                    'touchscreenRotation': config.TOUCHSCREEN_ROTATION,
                    'screenRotation': config.SCREEN_ROTATION,
                    'whiteList': {
                        'enabled': config.WHITE_LIST.get('ENABLED', False),
                        'urls': config.WHITE_LIST.get('URLS', []),
                        'iframeEnabled': config.WHITE_LIST.get('IFRAME_ENABLED', False)
                    },
                    'navBar': {
                        'enabled': config.NAV_BAR.get('ENABLED', False),
                        'enabledButtons': config.NAV_BAR.get('ENABLED_BUTTONS', []),
                        'horizontalPosition': config.NAV_BAR.get('HORIZONTAL_POSITION', 'center'),
                        'verticalPosition': config.NAV_BAR.get('VERTICAL_POSITION', 'bottom'),
                        'width': config.NAV_BAR.get('WIDTH', 100)
                    },
                    'virtualKeyboard': {
                        'enabled': config.VIRTUAL_KEYBOARD.get('ENABLED', False)
                    },
                    'screenSaver':  {
                        'enabled': config.SCREEN_SAVER.get('ENABLED', False),
                        'idleTime': config.SCREEN_SAVER.get('IDLE_TIME', 3600),
                        'text': config.SCREEN_SAVER.get('TEXT', 'Touch me')
                    }
                }

                out_json = json.dumps({
                    'event': 'onGetClientConfig',
                    'data': client_options
                })

                current_sum = hashlib.md5(out_json.encode()).hexdigest()
                if current_sum != last_sum:
                    last_sum = current_sum
                    resolve_rotation_config(config)
                    generate_xscreensaver_config(
                        os.path.join(user_home, '.xscreensaver'),
                        config.SCREEN_SAVER.get('ENABLED', False),
                        config.SCREEN_SAVER.get('IDLE_TIME', 3600),
                        config.SCREEN_SAVER.get('TEXT', 'Touch me')
                    )
                    await websocket.send(out_json)

            except websockets.ConnectionClosed as e:
                print(e)

            await asyncio.sleep(2)

    start_server = websockets.serve(config_watcher, "127.0.0.1", 5678)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


@command
def post_install():
    if not os.geteuid() == 0:
        sys.exit('Script must be run as root')
    config = parse_config()

    user_home = os.path.join('/', 'home', config.USER)

    try:
        uid = pwd.getpwnam(config.USER).pw_uid
    except KeyError:
        create_user(config.USER, user_home)
        set_user_groups(config.USER, ['video'])
        uid = pwd.getpwnam(config.USER).pw_uid
    gid = grp.getgrnam(config.USER).gr_gid

    # Create ~/.xinitrc
    xinitrc_content = [
        '#!/bin/sh',
        '# !!!! DO NOT EDIT THIS FILE IT IS AUTOGENERATED BY chromium-kiosk',
        'xset -dpms      # disable DPMS (Energy Star) features.',
        'xset s off      # disable screen saver',
        'xset s noblank  # don\'t blank the video device',
        'xscreensaver -no-splash & # xscreensaver daemon',
        'unclutter &     # hides your cursor after inactivity',
        'openbox &',
        'if [ -e ~/chromium-kiosk-prehook.sh ] # Check if prehook exists and run it',
        'then',
        '    ~/chromium-kiosk-prehook.sh',
        'fi',
        'exec chromium-kiosk run --config_prod --log_dir={} && killall -u $USER'.format(user_home)
    ]

    xinitrc_content_path = os.path.join(user_home, '.xinitrc')
    with open(xinitrc_content_path, 'w') as f:
        f.write('\n'.join(xinitrc_content))

    os.chown(xinitrc_content_path, uid, gid)
    os.chmod(xinitrc_content_path, 0o644)

    # Update ~/.bash_profile
    bashprofile_content = [
        '#',
        '# ~/.bash_profile',
        '#',
        '',
        '# !!!! DO NOT EDIT THIS FILE IT IS AUTOGENERATED BY chromium-kiosk',
        '[[ -f ~/.bashrc ]] && . ~/.bashrc',
        'if [ -z "$DISPLAY" ] && [ -n "$XDG_VTNR" ] && [ "$XDG_VTNR" -eq 1 ]; then',
        '   exec startx >& /dev/null',
        'fi'
    ]

    bashprofile_content_path = os.path.join(user_home, '.bash_profile')
    with open(bashprofile_content_path, 'w') as f:
        f.write('\n'.join(bashprofile_content))

    os.chown(bashprofile_content_path, uid, gid)
    os.chmod(bashprofile_content_path, 0o644)

    # Create ~/.hushlogin to hide last login message
    hushlogin_path = os.path.join(user_home, '.hushlogin')
    with open(hushlogin_path, 'w') as f: 
        pass

    os.chown(hushlogin_path, uid, gid)
    os.chmod(hushlogin_path, 0o644)

    # Update autologin service
    systemd_autologin = [
        '[Service]',
        'ExecStart=',
        'ExecStart=-{} --skip-login --nonewline --noissue --autologin {} --noclear %I $TERM'.format(shutil.which('agetty'), config.USER),
    ]

    getty_path = os.path.join('/', 'etc', 'systemd', 'system', 'getty@tty1.service.d', 'override.conf')
    getty_dir_path = os.path.dirname(getty_path)

    if not os.path.exists(getty_dir_path):
        os.makedirs(getty_dir_path)

    with open(getty_path, 'w') as f:
        f.write('\n'.join(systemd_autologin))

    # Generate .xscreensaverconfig
    xscreensaver_config_path = os.path.join(user_home, '.xscreensaver')
    generate_xscreensaver_config(
        xscreensaver_config_path,
        config.SCREEN_SAVER.get('ENABLED', False),
        config.SCREEN_SAVER.get('IDLE_TIME', 3600),
        config.SCREEN_SAVER.get('TEXT', 'Touch me'),
        reload_service=False
    )

    os.chown(xscreensaver_config_path, uid, gid)
    os.chmod(xscreensaver_config_path, 0o644)


@command
def system_info() -> None:
    primary_screen = detect_primary_screen()
    touchscreen_device = detect_touchscreen_device_name()

    info_items = {
        'Display': detect_display(),
        'Touchscreen device name': touchscreen_device,
        'Primary screen': primary_screen,
        'Screen rotation': get_screen_rotation(primary_screen),
        'Touchscreen rotation': get_touchscreen_rotation(touchscreen_device) if touchscreen_device else None,
    }

    for name, output in info_items.items():
        print('{}: {}'.format(name, output))


def main() -> None:
    signal.signal(signal.SIGINT, lambda *_: sys.exit(0))  # Properly handle Control+C
    getattr(command, 'chosen')()  # Execute the function specified by the user.


if __name__ == '__main__':
    main()
