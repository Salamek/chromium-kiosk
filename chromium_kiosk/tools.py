import os
import re
import subprocess
import datetime
import urllib.parse
from chromium_kiosk.enum.RotationEnum import RotationEnum
from xscreensaver_config.ConfigParser import ConfigParser
from typing import Union

rotation_to_xinput_coordinate = {
    RotationEnum.LEFT: '0 -1 1 1 0 0 0 0 1',
    RotationEnum.RIGHT: '0 1 0 -1 0 1 0 0 1',
    RotationEnum.NORMAL: '1 0 0 0 1 0 0 0 1',
    RotationEnum.INVERTED: '-1 0 1 0 -1 1 0 0 1'
}


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

    match_list = [b'touchscreen', b'touchcontroller', b'multi-touch', b'multitouch', b'raspberrypi-ts']
    for name in output:
        for match in match_list:
            if match in name.lower():
                return name.decode('UTF-8')

    return None


def detect_primary_screen() -> str:
    lines = subprocess.check_output(['xrandr', '--listactivemonitors']).splitlines()
    for line in lines:
        found = re.match(rb'^\s+(\d+):\s+(\S+)\s\S+\s+(\S+)$', line)
        if found:
            return found.group(3).decode('UTF-8')


def get_screen_rotation(screen: str) -> RotationEnum:
    check_display_env()
    lines = subprocess.check_output(['xrandr', '--current', '--verbose']).splitlines()
    for line in lines:
        result = re.match(r'^{}.+?(normal|left|inverted|right).+$'.format(screen), line.decode('UTF-8'))
        if result:
            return RotationEnum(result.group(1))
    return RotationEnum.NORMAL


def get_touchscreen_rotation(touch_device: str) -> RotationEnum:
    check_display_env()
    lines = subprocess.check_output(['xinput', 'list-props', touch_device]).splitlines()
    for line in lines:
        result = re.match(r'^\s+Coordinate\s+Transformation\s+Matrix\s+\(\d+\):\s+(.+)$', line.decode('UTF-8'))
        if result:
            int_list = ' '.join([str(int(float(item.strip()))) for item in result.group(1).split(',')])
            for rotation, value in rotation_to_xinput_coordinate.items():
                if value == int_list:
                    return rotation

    return RotationEnum.NORMAL


def rotate_display(rotation: RotationEnum, screen: str=None, touch_device: str=None) -> bool:
    return rotate_screen(rotation, screen) and rotate_touchscreen(rotation, touch_device)


def rotate_touchscreen(rotation: RotationEnum, touch_device: str=None) -> bool:
    check_display_env()

    if not touch_device:
        touch_device = detect_touchscreen_device_name()

    if not touch_device:
        return False

    current_rotation = get_touchscreen_rotation(touch_device)
    if current_rotation == rotation:
        return True

    command = [
        'xinput',
        'set-prop',
        '"{}"'.format(touch_device),
        '"Coordinate Transformation Matrix"',
        rotation_to_xinput_coordinate.get(rotation)
    ]

    return subprocess.call(' '.join(command), shell=True) == 0


def rotate_screen(rotation: RotationEnum, screen: str=None) -> bool:
    check_display_env()
    if not screen:
        screen = detect_primary_screen()

    if not screen:
        return False

    current_rotation = get_screen_rotation(screen)
    if current_rotation == rotation:
        return True

    if rotation not in list(RotationEnum):
        raise Exception('Rotation {} is not allowed'.format(rotation))

    return subprocess.call([
        'xrandr',
        '--output',
        screen,
        '--rotate',
        rotation.value
    ]) == 0


def generate_xscreensaver_config(config_path: str, enabled: bool, idle_time: int, text: str):
    xscreensaver_config_parser = ConfigParser(config_path)
    xscreensaver_config_parser.update({
        'timeout': str(datetime.timedelta(seconds=idle_time)),
        'cycle': '0',
        'lock': 'False',
        'visualID': 'default',
        'dpmsEnabled': 'False',
        'splash': 'False',
        'fade': 'True',
        'mode': 'one' if enabled else 'off',
        'selected': '0',
        'programs': [
            {
                'enabled': True,
                'renderer': 'GL',
                'command': 'chromium-kiosk screensaver --text=\'{}\''.format(text)
            }
        ]
    })
    xscreensaver_config_parser.save()

    # Reload xscreensaver config
    return subprocess.call([
        'xscreensaver-command',
        '--restart',
    ]) == 0