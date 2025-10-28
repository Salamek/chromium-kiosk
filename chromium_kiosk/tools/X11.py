from __future__ import annotations

import os
import re
import subprocess
from typing import TYPE_CHECKING

from chromium_kiosk.enum.RotationEnum import RotationEnum
from chromium_kiosk.tools import find_binary
from chromium_kiosk.tools.TouchDevice import TouchDevice
from chromium_kiosk.tools.WindowSystem import WindowSystem

if TYPE_CHECKING:
    from collections.abc import Generator


class X11(WindowSystem):
    rotation_to_xinput_coordinate: dict[RotationEnum, str]

    def __init__(self) -> None:
        self.rotation_to_xinput_coordinate = {
            RotationEnum.LEFT: "0 -1 1 1 0 0 0 0 1",
            RotationEnum.RIGHT: "0 1 0 -1 0 1 0 0 1",
            RotationEnum.NORMAL: "1 0 0 0 1 0 0 0 1",
            RotationEnum.INVERTED: "-1 0 1 0 -1 1 0 0 1",
        }

        self._check_display_env()

    def _check_display_env(self) -> None:
        if not os.getenv("DISPLAY"):
            # Display is not set, lets do that first
            display = self.detect_display()
            if not display:
                msg = "No display was detected! Are you running this under user with active X session?"
                raise ValueError(msg)
            os.environ["DISPLAY"] = display

    def _get_xinput_devices(self) -> Generator[TouchDevice, None, None]:
        binary_path = find_binary(["xinput"])
        if not binary_path:
            msg = "xinput binary was not found"
            raise FileNotFoundError(msg)

        output = subprocess.check_output([binary_path, "-list"]).splitlines()
        xinput_regex = re.compile(rb"^(?:[^\x00-\x7F]|\s)+(.+?)\s+id=(\d+)\s+\[.+]$")
        for line in output:
            result = xinput_regex.match(line)
            if result:
                name = result.group(1).decode("UTF-8")
                identifier = result.group(2).decode("UTF-8")
                yield TouchDevice(name=name, identifier=identifier)

    def detect_display(self) -> str | None:
        display = os.getenv("DISPLAY")
        if display:
            return display

        binary_path = find_binary(["ps"])
        if not binary_path:
            msg = "ps binary was not found"
            raise FileNotFoundError(msg)

        user_name = os.getenv("USER")
        if not user_name:
            msg = "USER env var is empty or not set"
            raise FileNotFoundError(msg)

        output = subprocess.check_output([binary_path, "e", "-u", user_name])
        result = re.search(r"DISPLAY=([.0-9A-Za-z:]*)", output.decode("UTF-8"), re.MULTILINE)
        if not result:
            return None
        return result.group(1)

    def find_touchscreen_device(self, force_device_name: str | None = None) -> TouchDevice | None:
        xinput_devices = self._get_xinput_devices()

        match_list = ["touchscreen", "touchcontroller", "multi-touch", "multitouch", "raspberrypi-ts", "touch"]
        for xinput_device in xinput_devices:

            if force_device_name and force_device_name == xinput_device.name:
                return xinput_device

            for match in match_list:
                if match in xinput_device.name.lower():
                    return xinput_device

        return None

    def detect_primary_screen(self) -> str | None:
        binary_path = find_binary(["xrandr"])
        if not binary_path:
            msg = "xrandr binary was not found"
            raise FileNotFoundError(msg)
        lines = subprocess.check_output([binary_path, "--listactivemonitors"]).splitlines()
        for line in lines:
            found = re.match(rb"^\s+(\d+):\s+(\S+)\s\S+\s+(\S+)$", line)
            if found:
                return found.group(3).decode("UTF-8")

        return None

    def get_screen_rotation(self, screen: str) -> RotationEnum:
        binary_path = find_binary(["xrandr"])
        if not binary_path:
            msg = "xrandr binary was not found"
            raise FileNotFoundError(msg)

        lines = subprocess.check_output([binary_path, "--current", "--verbose"]).splitlines()
        for line in lines:
            result = re.match(rf"^{screen}.+?(normal|left|inverted|right).+$", line.decode("UTF-8"))
            if result:
                return RotationEnum(result.group(1))
        return RotationEnum.NORMAL

    def get_touchscreen_rotation(self, touch_device: TouchDevice) -> RotationEnum:
        binary_path = find_binary(["xinput"])
        if not binary_path:
            msg = "xinput binary was not found"
            raise FileNotFoundError(msg)

        lines = subprocess.check_output([binary_path, "list-props", touch_device.identifier]).splitlines()
        for line in lines:
            result = re.match(r"^\s+Coordinate\s+Transformation\s+Matrix\s+\(\d+\):\s+(.+)$", line.decode("UTF-8"))
            if result:
                int_list = " ".join([str(int(float(item.strip()))) for item in result.group(1).split(",")])
                for rotation, value in self.rotation_to_xinput_coordinate.items():
                    if value == int_list:
                        return rotation

        return RotationEnum.NORMAL

    def rotate_display(
        self,
        rotation: RotationEnum,
        screen: str | None = None,
        force_touchscreen_name: str | None = None,
    ) -> bool:
        return self.rotate_screen(rotation, screen) and self.rotate_touchscreen(rotation, force_touchscreen_name)

    def rotate_touchscreen(self, rotation: RotationEnum, force_device_name: str | None = None) -> bool:
        touch_device = self.find_touchscreen_device(force_device_name)

        if not touch_device:
            return False

        current_rotation = self.get_touchscreen_rotation(touch_device)
        if current_rotation == rotation:
            return True

        binary_path = find_binary(["xinput"])
        if not binary_path:
            msg = "xinput binary was not found"
            raise FileNotFoundError(msg)

        rotation_matrix = self.rotation_to_xinput_coordinate.get(rotation)
        if not rotation_matrix:
            msg = "unknown rotation"
            raise ValueError(msg)

        command = [
            binary_path,
            "set-prop",
            touch_device.identifier,
            '"Coordinate Transformation Matrix"',
            rotation_matrix,
        ]

        return subprocess.call(" ".join(command), shell=True) == 0

    def rotate_screen(self, rotation: RotationEnum, screen: str | None = None) -> bool:

        if not screen:
            screen = self.detect_primary_screen()

        if not screen:
            return False

        current_rotation = self.get_screen_rotation(screen)
        if current_rotation == rotation:
            return True

        if rotation not in list(RotationEnum):
            msg = f"Rotation {rotation} is not allowed"
            raise ValueError(msg)

        binary_path = find_binary(["xrandr"])
        if not binary_path:
            msg = "xrandr binary was not found"
            raise FileNotFoundError(msg)

        return subprocess.call([
            binary_path,
            "--output",
            screen,
            "--rotate",
            rotation.value,
        ]) == 0
