import os
import re
import subprocess
import urllib.parse
from typing import Union


def check_display_env():
    if not os.getenv('DISPLAY'):
        # Display is not set, lets do that first
        os.environ['DISPLAY'] = detect_display()


def create_user(username: str, home: str) -> int:
    return subprocess.call([
        'useradd',
        '--system',
        '--user-group',
        '--shell',
        '/bin/bash',
        '--home-dir',
        home,
        '--create-home',
        username
    ])


def set_user_groups(username: str, groups: list):
    for group in groups:
        command = ['usermod', '-aG', group, username]
        subprocess.call(command)


def inject_parameters_to_url(url: str, parameters: dict) -> str:

    url_parts = list(urllib.parse.urlparse(url))
    query = dict(urllib.parse.parse_qsl(url_parts[4]))
    query.update(parameters)

    url_parts[4] = urllib.parse.urlencode(query)

    return urllib.parse.urlunparse(url_parts)


def detect_display():
    display = os.getenv('DISPLAY')
    if display:
        return display

    output = subprocess.check_output(['ps', 'e', '-u', os.getenv('USER')])
    result = re.search(r'DISPLAY=([\.0-9A-Za-z:]*)', output.decode('UTF-8'), re.MULTILINE)
    return result.group(1)


def detect_touchscreen_device_name() -> Union[str, None]:
    check_display_env()
    output = subprocess.check_output(['xinput', '-list', '--name-only']).splitlines()

    match_list = [b'touchscreen', b'touchcontroller', b'multi-touch', b'multitouch']
    for name in output:
        for match in match_list:
            if match in name.lower():
                return name.decode('UTF-8')

    return None


def detect_primary_screen() -> str:
    check_display_env()
    lines = subprocess.check_output(['xrandr', '--current']).splitlines()
    for line in lines:
        if b'primary' in line:
            return line.split()[0].decode('UTF-8')


def get_screen_rotation(screen: str) -> str:
    check_display_env()
    lines = subprocess.check_output(['xrandr', '--current', '--verbose']).splitlines()
    for line in lines:
        if b'primary' in line:
            result = re.search(rb'(normal|left|inverted|right)', line)
            if not result:
                return 'normal'
            return result.group(1).decode('UTF-8')


def rotate_screen(rotation: str, screen: str=None, touch_device: str=None) -> bool:
    check_display_env()
    if not screen:
        screen = detect_primary_screen()

    current_rotation = get_screen_rotation(screen)
    if current_rotation == rotation:
        return True

    if not touch_device:
        touch_device = detect_touchscreen_device_name()

    allowed_rotations = ['left', 'right', 'normal', 'inverted']
    if rotation not in allowed_rotations:
        raise Exception('Rotation {} is not allowed'.format(rotation))

    rotation_to_xinput_coordinate = {
        'left': '0 -1 1 1 0 0 0 0 1',
        'right': '0 1 0 -1 0 1 0 0 1',
        'normal': '1 0 0 0 1 0 0 0 1',
        'inverted': '-1 0 1 0 -1 1 0 0 1'
    }

    xrandr_ok = subprocess.call([
        'xrandr',
        '--output',
        screen,
        '--rotate',
        rotation
    ]) == 0

    if touch_device:
        command = [
            'xinput',
            'set-prop',
            '"{}"'.format(touch_device),
            '"Coordinate Transformation Matrix"',
            rotation_to_xinput_coordinate.get(rotation)
        ]

        xinput_ok = subprocess.call(' '.join(command), shell=True) == 0
    else:
        xinput_ok = True

    return xrandr_ok and xinput_ok
