import os
import re
import subprocess
import urllib.parse
from typing import Union


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
    if not os.getenv('DISPLAY'):
        # Display is not set, lets do that first
        os.environ['DISPLAY'] = detect_display()
    output = subprocess.check_output(['xinput', '-list', '--name-only']).splitlines()

    match_list = ['touchscreen', 'touchcontroller']
    touchscreen_name = None
    for name in output:
        for match in match_list:
            if match in name.lower():
                touchscreen_name = name
                break

    return touchscreen_name


def rotate_screen(rotation: str) -> bool:
    if not os.getenv('DISPLAY'):
        # Display is not set, lets do that first
        os.environ['DISPLAY'] = detect_display()

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
        '-o',
        rotation
    ]) == 0

    device_name = detect_touchscreen_device_name()
    if device_name:
        xinput_ok = subprocess.call([
            'xinput',
            'set-prop',
            device_name,
            '--type=float',
            '"Coordinate Transformation Matrix"',
            rotation_to_xinput_coordinate.get(rotation)
        ]) == 0
    else:
        xinput_ok = True

    return xrandr_ok and xinput_ok
