from __future__ import annotations

from typing import TYPE_CHECKING

from chromium_kiosk.enum.RotationEnum import RotationEnum
from chromium_kiosk.tools.WindowSystem import WindowSystem

if TYPE_CHECKING:
    from chromium_kiosk.tools.TouchDevice import TouchDevice


class Wayland(WindowSystem):
    def detect_display(self) -> str | None:
        return None

    def find_touchscreen_device(self, force_device_name: str | None = None) -> TouchDevice | None:
        _ = force_device_name
        return None

    def detect_primary_screen(self) -> str | None:
        return None

    def get_screen_rotation(self, screen: str) -> RotationEnum:
        _ = screen
        return RotationEnum.NORMAL

    def get_touchscreen_rotation(self, touch_device: TouchDevice) -> RotationEnum:
        _ = touch_device
        return RotationEnum.NORMAL

    def rotate_display(self, rotation: RotationEnum, screen: str | None = None, force_touchscreen_name: str | None = None) -> bool:
        _ = rotation
        _ = screen
        _ = force_touchscreen_name
        return True

    def rotate_touchscreen(self, rotation: RotationEnum, force_device_name: str | None = None) -> bool:
        _ = rotation
        _ = force_device_name
        return True

    def rotate_screen(self, rotation: RotationEnum, screen: str | None = None) -> bool:
        _ = rotation
        _ = screen
        return True
