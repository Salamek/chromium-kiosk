import os
import re
import subprocess
import shutil
import urllib.parse
import dataclasses
from chromium_kiosk.enum.RotationEnum import RotationEnum
from typing import List, Optional, Iterator

rotation_to_xinput_coordinate = {
    RotationEnum.LEFT: '0 -1 1 1 0 0 0 0 1',
    RotationEnum.RIGHT: '0 1 0 -1 0 1 0 0 1',
    RotationEnum.NORMAL: '1 0 0 0 1 0 0 0 1',
    RotationEnum.INVERTED: '-1 0 1 0 -1 1 0 0 1'
}

@dataclasses.dataclass
class TouchDevice:
    name: bytes
    xinput_id: int


def check_display_env() -> None:
    if not os.getenv('DISPLAY'):
        # Display is not set, lets do that first
        display = detect_display()
        if not display:
            raise Exception('No display was detected! Are you running this under user with active X session?')
        os.environ['DISPLAY'] = display


def inject_parameters_to_url(url: str, parameters: dict) -> str:

    url_parts = list(urllib.parse.urlparse(url))
    query = dict(urllib.parse.parse_qsl(url_parts[4]))
    query.update(parameters)

    url_parts[4] = urllib.parse.urlencode(query)

    return urllib.parse.urlunparse(url_parts)


def detect_display() -> Optional[str]:
    display = os.getenv('DISPLAY')
    if display:
        return display

    output = subprocess.check_output(['ps', 'e', '-u', os.getenv('USER')])
    result = re.search(r'DISPLAY=([\.0-9A-Za-z:]*)', output.decode('UTF-8'), re.MULTILINE)
    if not result:
        return None
    return result.group(1)


def get_xinput_devices() -> Iterator[TouchDevice]:
    check_display_env()
    output = subprocess.check_output(['xinput', '-list']).splitlines()
    xinput_regex = re.compile(rb"^(?:[^\x00-\x7F]|\s)+(.+?)\s+id=(\d+)\s+\[.+\]$")
    for line in output:
        result = xinput_regex.match(line)
        if result:
            name = result.group(1)
            xinput_id = int(result.group(2))
            yield TouchDevice(name=name, xinput_id=xinput_id)


def find_touchscreen_device(force_device_name: Optional[str] = None) -> Optional[TouchDevice]:
    xinput_devices = get_xinput_devices()

    match_list = [b'touchscreen', b'touchcontroller', b'multi-touch', b'multitouch', b'raspberrypi-ts', b'touch']
    for xinput_device in xinput_devices:

        if force_device_name and force_device_name == xinput_device.name:
            return xinput_device

        for match in match_list:
            if match in xinput_device.name.lower():
                return xinput_device



def detect_primary_screen() -> Optional[str]:
    check_display_env()
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


def get_touchscreen_rotation(touch_device: int) -> RotationEnum:
    check_display_env()
    lines = subprocess.check_output(['xinput', 'list-props', str(touch_device)]).splitlines()
    for line in lines:
        result = re.match(r'^\s+Coordinate\s+Transformation\s+Matrix\s+\(\d+\):\s+(.+)$', line.decode('UTF-8'))
        if result:
            int_list = ' '.join([str(int(float(item.strip()))) for item in result.group(1).split(',')])
            for rotation, value in rotation_to_xinput_coordinate.items():
                if value == int_list:
                    return rotation

    return RotationEnum.NORMAL


def rotate_display(rotation: RotationEnum, screen: Optional[str] = None, force_touchscreen_name: Optional[str] = None) -> bool:
    return rotate_screen(rotation, screen) and rotate_touchscreen(rotation, force_touchscreen_name)


def rotate_touchscreen(rotation: RotationEnum, force_device_name: Optional[str] = None) -> bool:
    check_display_env()

    touch_device = find_touchscreen_device(force_device_name)

    if not touch_device:
        return False

    current_rotation = get_touchscreen_rotation(touch_device.xinput_id)
    if current_rotation == rotation:
        return True

    command = [
        'xinput',
        'set-prop',
        str(touch_device.xinput_id),
        '"Coordinate Transformation Matrix"',
        rotation_to_xinput_coordinate.get(rotation)
    ]

    return subprocess.call(' '.join(command), shell=True) == 0


def rotate_screen(rotation: RotationEnum, screen: Optional[str] = None) -> bool:
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


def find_binary(names: List[str]) -> Optional[str]:
    """
    Find binary
    :return:
    """
    for name in names:
        found = shutil.which(name)
        if found:
            return found
