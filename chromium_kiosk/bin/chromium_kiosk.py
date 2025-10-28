#!/usr/bin/env python3
"""Main entry-point into the 'Chromium Kiosk' application.

This is Chromium Kiosk.

License: GPL-3.0
Website: https://github.com/Salamek/chromium-kiosk

Command details:
    run                 Run the application.
Usage:
    chromium-kiosk run [-l DIR] [--config_prod]
    chromium-kiosk watch_config [--config_prod]
    chromium-kiosk system_info [--config_prod]
    chromium-kiosk (-h | --help)

Options:
    --config_prod               Load the production configuration instead of dev
    -l DIR --log_dir=DIR        Directory to log into
"""
from __future__ import annotations

import json
import logging
import logging.handlers
import os
import signal
import sys
import time
from functools import wraps
from importlib import import_module
from pathlib import Path
from typing import Callable, ClassVar, TypeVar

import yaml
from docopt import docopt
from watchdog import events
from watchdog.observers import Observer
from websocket import create_connection

import chromium_kiosk as app_root
from chromium_kiosk.config import Config
from chromium_kiosk.enum.RotationEnum import RotationEnum
from chromium_kiosk.Qiosk import Qiosk

if not os.getenv("WAYLAND_DISPLAY"):
    from chromium_kiosk.tools.X11 import X11 as WindowSystem  # noqa: N811
else:
    from chromium_kiosk.tools.Wayland import Wayland as WindowSystem


CT = TypeVar("CT")

OPTIONS = docopt(__doc__)
APP_ROOT_FOLDER = Path(app_root.__file__).parent.absolute()


def resolve_rotation_config(options: Config) -> None:
    window_system = WindowSystem()
    # Rotation options are set separately, use them
    if options.TOUCHSCREEN_ROTATION and options.SCREEN_ROTATION:
        window_system.rotate_screen(RotationEnum(options.SCREEN_ROTATION))
        window_system.rotate_touchscreen(RotationEnum(options.TOUCHSCREEN_ROTATION), options.TOUCHSCREEN)
    elif not options.TOUCHSCREEN_ROTATION and options.SCREEN_ROTATION:
        window_system.rotate_screen(RotationEnum(options.SCREEN_ROTATION))
        window_system.rotate_touchscreen(RotationEnum.NORMAL, options.TOUCHSCREEN)
    elif options.TOUCHSCREEN_ROTATION and not options.SCREEN_ROTATION:
        window_system.rotate_screen(RotationEnum.NORMAL)
        window_system.rotate_touchscreen(RotationEnum(options.TOUCHSCREEN_ROTATION), options.TOUCHSCREEN)
    elif options.DISPLAY_ROTATION:
        window_system.rotate_display(RotationEnum(options.DISPLAY_ROTATION), force_touchscreen_name=options.TOUCHSCREEN)
    else:
        # just fallback to normal
        window_system.rotate_display(RotationEnum.NORMAL, force_touchscreen_name=options.TOUCHSCREEN)


class CustomFormatter(logging.Formatter):
    LEVEL_MAP: ClassVar[dict[int, str]] = {logging.FATAL: "F", logging.ERROR: "E", logging.WARNING: "W", logging.INFO: "I", logging.DEBUG: "D"}

    def format(self, record: logging.LogRecord) -> str:
        record.levelletter = self.LEVEL_MAP[record.levelno]
        return super().format(record)


def setup_logging(name: str | None = None, level: int = logging.DEBUG) -> None:
    """Setup Google-Style logging for the entire application.

    At first I hated this but I had to use it for work, and now I prefer it. Who knew?
    From: https://github.com/twitter/commons/blob/master/src/python/twitter/common/log/formatters/glog.py

    Always logs DEBUG statements somewhere.

    Positional arguments:
    name -- Append this string to the log file filename.
    """

    fmt = "%(levelletter)s%(asctime)s.%(msecs).03d %(process)d %(filename)s:%(lineno)d] %(message)s"
    datefmt = "%m%d %H:%M:%S"
    formatter = CustomFormatter(fmt, datefmt)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(console_handler)

    if OPTIONS["--log_dir"]:
        log_dir = Path(OPTIONS["--log_dir"])
        if not log_dir.is_dir():
            print(f"ERROR: Directory {log_dir} does not exist.")
            sys.exit(1)
        if not os.access(log_dir, os.W_OK):
            print(f"ERROR: No permissions to write to directory {log_dir}.")
            sys.exit(1)

        file_name = log_dir.joinpath(f"chromium_kiosk_{name}.log")
        file_handler = logging.handlers.TimedRotatingFileHandler(file_name, when="d", backupCount=7)
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)



def find_config_files(yaml_files: list[str] | None = None) -> list[str]:
    return yaml_files or [f for f in [
        Path("/etc/chromium-kiosk/config.yml"),
        # Compability with old proprietary version
        Path("/etc/granad-kiosk/config.yml"),
        APP_ROOT_FOLDER.joinpath("..", "config.yml").absolute(),
        APP_ROOT_FOLDER.joinpath("config.yml"),
    ] if f.is_file()]


def get_config(config_class_string: str, yaml_files: list[Path] | None = None) -> Config:
    """Load the Flask config from a class.
    Positional arguments:
    config_class_string -- string representation of a configuration class that will be loaded (e.g.
        'pypi_portal.config.Production').
    yaml_files -- List of YAML files to load. This is for testing, leave None in dev/production.
    Returns:
    A class object to be fed into app.config.from_object().
    """
    config_module, config_class = config_class_string.rsplit(".", 1)
    config_obj = getattr(import_module(config_module), config_class)

    # Load additional configuration settings.
    yaml_files = find_config_files(yaml_files)
    additional_dict = {}
    for y in yaml_files:
        with y.open("r", encoding="UTF-8") as f:
            loaded_data = yaml.safe_load(f)
            if isinstance(loaded_data, dict):
                additional_dict.update(loaded_data)
            else:
                msg = f"Failed to parse configuration {y}"
                raise TypeError(msg)

    # Merge the rest into the Flask app config.
    for key, value in additional_dict.items():
        setattr(config_obj, key, value)

    return config_obj



def parse_config() -> Config:
    """Parses command line options for Flask.

    Returns:
    Config instance to pass into create_app().
    """
    # Figure out which class will be imported.
    config_class_string = "chromium_kiosk.config.Production" if OPTIONS["--config_prod"] else "chromium_kiosk.config.Config"
    config_obj = get_config(config_class_string)

    if config_obj.FULL_SCREEN:  # @TODO remove in next minor version
        config_obj.WINDOW_MODE = "fullscreen"

    return config_obj



def command(name: str | None = None) -> Callable[[Callable[..., CT]], Callable[..., CT]]:
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

    def function_wrap(func: Callable[..., CT]) -> Callable[..., CT]:

        @wraps(func)
        def wrapped() -> CT:
            return func()

        command_name = name if name else func.__name__

        # Register chosen function.
        if command_name not in OPTIONS:
            msg = f"Cannot register {command_name}, not mentioned in docstring/docopt."
            raise KeyError(msg)
        if OPTIONS[command_name]:
            command.chosen = func  # type: ignore[attr-defined]

        return wrapped

    return function_wrap



@command()
def run() -> None:
    config = parse_config()
    setup_logging("kiosk", logging.DEBUG if config.DEBUG else logging.WARNING)

    # Rotate screen by config value
    resolve_rotation_config(config)

    selected_browser = Qiosk(config)
    selected_browser.run()


@command()
def watch_config() -> None:
    config = parse_config()
    setup_logging("watch_config", logging.DEBUG if config.DEBUG else logging.WARNING)
    log = logging.getLogger(__name__)

    class ConfigEventHandler(events.FileSystemEventHandler):
        def __init__(self) -> None:
            parsed_config = parse_config()
            current_config = Qiosk.resolve_command_mappings_config(parsed_config)
            log.debug("Current config: %s", str(current_config))
            self.current_config = current_config

        def on_modified(self, _event: events.DirModifiedEvent | events.FileModifiedEvent) -> None:
            raw_config = parse_config()
            check_config = Qiosk.resolve_command_mappings_config(raw_config)
            log.debug("New config: %s", str(check_config))
            diffs = Qiosk.diff_command_mappings_config_value(self.current_config, check_config)

            if diffs:
                log.debug(diffs)
                resolve_rotation_config(raw_config)

                for command_name, config_value in diffs.items():
                    # Emit changes
                    payload = {
                        "command": command_name,
                        "data": config_value.payload,
                    }

                    ws = create_connection("ws://localhost:1791")
                    ws.send(json.dumps(payload))
                    result = ws.recv()
                    ws.close()

                    log.debug(result)


                # Set new config as old
                self.current_config = check_config

    event_handler = ConfigEventHandler()

    observer = Observer()
    for config_file_path in find_config_files():
        try:
            observer.schedule(event_handler, config_file_path, recursive=False, event_filter=[events.FileModifiedEvent])
        except TypeError:  # noqa: PERF203
            # Support for older versions
            observer.schedule(event_handler, config_file_path, recursive=False)

    observer.start()
    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()



@command()
def system_info() -> None:
    config = parse_config()
    setup_logging("system_info", logging.DEBUG if config.DEBUG else logging.WARNING)
    window_system = WindowSystem()
    primary_screen = window_system.detect_primary_screen()
    touchscreen_device = window_system.find_touchscreen_device(config.TOUCHSCREEN)

    info_items = {
        "Display": window_system.detect_display(),
        "Touchscreen device": touchscreen_device,
        "Primary screen": primary_screen,
        "Screen rotation": window_system.get_screen_rotation(primary_screen),
        "Touchscreen rotation": window_system.get_touchscreen_rotation(touchscreen_device) if touchscreen_device else None,
    }

    for name, output in info_items.items():
        print(f"{name}: {output}")


def main() -> None:
    signal.signal(signal.SIGINT, lambda *_: sys.exit(0))  # Properly handle Control+C
    command.chosen()  # Execute the function specified by the user.


if __name__ == "__main__":
    main()
