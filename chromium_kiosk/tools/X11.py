import os
import re
import subprocess
from typing import Optional, Iterator

from chromium_kiosk.enum.RotationEnum import RotationEnum
from chromium_kiosk.tools.TouchDevice import TouchDevice
from chromium_kiosk.tools.WindowSystem import WindowSystem


class X11(WindowSystem):
    rotation_to_xinput_coordinate = {
        RotationEnum.LEFT: '0 -1 1 1 0 0 0 0 1',
        RotationEnum.RIGHT: '0 1 0 -1 0 1 0 0 1',
        RotationEnum.NORMAL: '1 0 0 0 1 0 0 0 1',
        RotationEnum.INVERTED: '-1 0 1 0 -1 1 0 0 1'
    }

    def __init__(self):
        self._check_display_env()

    def _check_display_env(self) -> None:
        if not os.getenv('DISPLAY'):
            # Display is not set, lets do that first
            display = self.detect_display()
            if not display:
                raise Exception('No display was detected! Are you running this under user with active X session?')
            os.environ['DISPLAY'] = display

    def _get_xinput_devices(self) -> Iterator[TouchDevice]:
        output = subprocess.check_output(['xinput', '-list']).splitlines()
        xinput_regex = re.compile(rb"^(?:[^\x00-\x7F]|\s)+(.+?)\s+id=(\d+)\s+\[.+]$")
        for line in output:
            result = xinput_regex.match(line)
            if result:
                name = result.group(1).decode("UTF-8")
                identifier = result.group(2).decode("UTF-8")
                yield TouchDevice(name=name, identifier=identifier)

    def detect_display(self) -> Optional[str]:
        display = os.getenv('DISPLAY')
        if display:
            return display

        output = subprocess.check_output(['ps', 'e', '-u', os.getenv('USER')])
        result = re.search(r'DISPLAY=([.0-9A-Za-z:]*)', output.decode('UTF-8'), re.MULTILINE)
        if not result:
            return None
        return result.group(1)

    def find_touchscreen_device(self, force_device_name: Optional[str] = None) -> Optional[TouchDevice]:
        xinput_devices = self._get_xinput_devices()

        match_list = ["touchscreen", "touchcontroller", "multi-touch", "multitouch", "raspberrypi-ts", "touch"]
        for xinput_device in xinput_devices:

            if force_device_name and force_device_name == xinput_device.name:
                return xinput_device

            for match in match_list:
                if match in xinput_device.name.lower():
                    return xinput_device

    def detect_primary_screen(self) -> Optional[str]:
        lines = subprocess.check_output(['xrandr', '--listactivemonitors']).splitlines()
        for line in lines:
            found = re.match(rb'^\s+(\d+):\s+(\S+)\s\S+\s+(\S+)$', line)
            if found:
                return found.group(3).decode('UTF-8')

    def get_screen_rotation(self, screen: str) -> RotationEnum:
        lines = subprocess.check_output(['xrandr', '--current', '--verbose']).splitlines()
        for line in lines:
            result = re.match(r'^{}.+?(normal|left|inverted|right).+$'.format(screen), line.decode('UTF-8'))
            if result:
                return RotationEnum(result.group(1))
        return RotationEnum.NORMAL

    def get_touchscreen_rotation(self, touch_device: TouchDevice) -> RotationEnum:
        lines = subprocess.check_output(['xinput', 'list-props', touch_device.identifier]).splitlines()
        for line in lines:
            result = re.match(r'^\s+Coordinate\s+Transformation\s+Matrix\s+\(\d+\):\s+(.+)$', line.decode('UTF-8'))
            if result:
                int_list = ' '.join([str(int(float(item.strip()))) for item in result.group(1).split(',')])
                for rotation, value in self.rotation_to_xinput_coordinate.items():
                    if value == int_list:
                        return rotation

        return RotationEnum.NORMAL

    def rotate_display(self, rotation: RotationEnum, screen: Optional[str] = None,
                       force_touchscreen_name: Optional[str] = None) -> bool:
        return self.rotate_screen(rotation, screen) and self.rotate_touchscreen(rotation, force_touchscreen_name)

    def rotate_touchscreen(self, rotation: RotationEnum, force_device_name: Optional[str] = None) -> bool:
        touch_device = self.find_touchscreen_device(force_device_name)

        if not touch_device:
            return False

        current_rotation = self.get_touchscreen_rotation(touch_device)
        if current_rotation == rotation:
            return True

        command = [
            'xinput',
            'set-prop',
            touch_device.identifier,
            '"Coordinate Transformation Matrix"',
            self.rotation_to_xinput_coordinate.get(rotation)
        ]

        return subprocess.call(' '.join(command), shell=True) == 0

    def rotate_screen(self, rotation: RotationEnum, screen: Optional[str] = None) -> bool:

        if not screen:
            screen = self.detect_primary_screen()

        if not screen:
            return False

        current_rotation = self.get_screen_rotation(screen)
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
