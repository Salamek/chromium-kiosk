#!/usr/bin/env python3
"""Main entry-point into the 'Granad Kiosk' application.

This is BESY Granad Kiosk.

License: PROPRIETARY
Website: git@gitlab.salamek.cz:sadam/granad-kiosk.git

Command details:
    run                 Run the application.
    post_install        Post install hook.
Usage:
    granad-kiosk run [-l DIR] [--config_prod]
    granad-kiosk post_install [--config_prod]
    granad-kiosk (-h | --help)

Options:
    --config_prod               Load the production configuration instead of dev
    -l DIR --log_dir=DIR        Directory to log into
"""

from __future__ import print_function

import logging
import logging.handlers
import os
import pwd
import grp
import signal
import sys
from functools import wraps
from importlib import import_module
from granad_kiosk.Chromium import Chromium
from granad_kiosk.tools import create_user
import granad_kiosk as app_root

import yaml
from docopt import docopt

OPTIONS = docopt(__doc__)
APP_ROOT_FOLDER = os.path.abspath(os.path.dirname(app_root.__file__))


class CustomFormatter(logging.Formatter):
    LEVEL_MAP = {logging.FATAL: 'F', logging.ERROR: 'E', logging.WARN: 'W', logging.INFO: 'I', logging.DEBUG: 'D'}

    def format(self, record):
        record.levelletter = self.LEVEL_MAP[record.levelno]
        return super(CustomFormatter, self).format(record)


def setup_logging(name=None, level=logging.DEBUG):
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
        file_name = os.path.join(OPTIONS['--log_dir'], 'granad_kiosk_{}.log'.format(name))
        file_handler = logging.handlers.TimedRotatingFileHandler(file_name, when='d', backupCount=7)
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)


def get_config(config_class_string, yaml_files=None):
    """Load the Flask config from a class.
    Positional arguments:
    config_class_string -- string representation of a configuration class that will be loaded (e.g.
        'pypi_portal.config.Production').
    yaml_files -- List of YAML files to load. This is for testing, leave None in dev/production.
    Returns:
    A class object to be fed into app.config.from_object().
    """
    config_module, config_class = config_class_string.rsplit('.', 1)
    config_obj = getattr(import_module(config_module), config_class)

    # Expand some options.
    db_fmt = 'granad_kiosk.models.{}'
    if getattr(config_obj, 'DB_MODELS_IMPORTS', False):
        config_obj.DB_MODELS_IMPORTS = [db_fmt.format(m) for m in config_obj.DB_MODELS_IMPORTS]

    # Load additional configuration settings.
    yaml_files = yaml_files or [f for f in [
        os.path.join('/', 'etc', 'granad-kiosk', 'config.yml'),
        os.path.abspath(os.path.join(APP_ROOT_FOLDER, '..', 'config.yml')),
        os.path.join(APP_ROOT_FOLDER, 'config.yml'),
    ] if os.path.exists(f)]
    additional_dict = dict()
    for y in yaml_files:
        with open(y) as f:
            loaded_data = yaml.load(f.read())
            if isinstance(loaded_data, dict):
                additional_dict.update(loaded_data)
            else:
                raise Exception('Failed to parse configuration {}'.format(y))

    # Merge the rest into the Flask app config.
    for key, value in additional_dict.items():
        setattr(config_obj, key, value)

    return config_obj


def parse_options():
    """Parses command line options for Flask.

    Returns:
    Config instance to pass into create_app().
    """
    # Figure out which class will be imported.
    if OPTIONS['--config_prod']:
        config_class_string = 'granad_kiosk.config.Production'
    else:
        config_class_string = 'granad_kiosk.config.Config'
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
    options = parse_options()
    setup_logging('kiosk', logging.DEBUG if options.DEBUG else logging.WARNING)
    chromium = Chromium()
    if options.KIOSK:
        chromium.set_kiosk(True)

    if options.CLEAN_START:
        chromium.clean_start()

    chromium.set_urls(options.URLS)
    chromium.run()


@command
def post_install():
    if not os.geteuid() == 0:
        sys.exit('Script must be run as root')
    options = parse_options()

    user_home = os.path.join('/', 'home', options.USER)

    try:
        uid = pwd.getpwnam(options.USER).pw_uid
    except KeyError:
        create_user(options.USER, user_home)
        uid = pwd.getpwnam(options.USER).pw_uid
    gid = grp.getgrnam(options.USER).gr_gid

    # Create ~/.xinitrc
    xinitrc_content = [
        '#!/bin/sh',
        '# !!!! DO NOT EDIT THIS FILE IT IS AUTOGENERATED BY granad-kiosk',
        'xset -dpms      # disable DPMS (Energy Star) features.',
        'xset s off      # disable screen saver',
        'xset s noblank  # don\'t blank the video device',
        'unclutter &     # hides your cursor after inactivity',
        'matchbox-window-manager &',
        'exec granad-kiosk run --config_prod --log_dir={}'.format(user_home),
        'reboot'
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
        '#'
        '# !!!! DO NOT EDIT THIS FILE IT IS AUTOGENERATED BY granad-kiosk',
        '[[ -f ~/.bashrc ]] && . ~/.bashrc',
        'if [-z "$DISPLAY"] & & [-n "$XDG_VTNR"] & & ["$XDG_VTNR" - eq 1]; then',
        '   exec startx',
        'fi'
    ]

    bashprofile_content_path = os.path.join(user_home, '.bash_profile')
    with open(bashprofile_content_path, 'w') as f:
        f.write('\n'.join(bashprofile_content))

    os.chown(bashprofile_content_path, uid, gid)
    os.chmod(bashprofile_content_path, 0o644)

    # Update autologin service
    systemd_autologin = [
        '[Service]',
        'ExecStart=',
        'ExecStart=-/usr/bin/agetty --autologin {} --noclear %I $TERM'.format(options.USER),
    ]

    getty_path = os.path.join('/', 'etc', 'systemd', 'system', 'getty@tty1.service.d', 'override.conf')
    getty_dir_path = os.path.dirname(getty_path)

    if not os.path.exists(getty_dir_path):
        os.makedirs(getty_dir_path)

    with open(getty_path, 'w') as f:
        f.write('\n'.join(systemd_autologin))


def main():
    signal.signal(signal.SIGINT, lambda *_: sys.exit(0))  # Properly handle Control+C
    getattr(command, 'chosen')()  # Execute the function specified by the user.


if __name__ == '__main__':
    main()

