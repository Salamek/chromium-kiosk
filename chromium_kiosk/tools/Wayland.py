from __future__ import annotations

from chromium_kiosk.enum.RotationEnum import RotationEnum
from chromium_kiosk.tools.TouchDevice import TouchDevice
from chromium_kiosk.tools.WindowSystem import WindowSystem


class Wayland(WindowSystem):
    def detect_display(self) -> str | None:
        pass

    def find_touchscreen_device(self, force_device_name: str | None = None) -> TouchDevice | None:
        pass

    def detect_primary_screen(self) -> str | None:
        pass

    def get_screen_rotation(self, screen: str) -> RotationEnum:
        pass

    def get_touchscreen_rotation(self, touch_device: TouchDevice) -> RotationEnum:
        pass

    def rotate_display(self, rotation: RotationEnum, screen: str | None = None,
                       force_touchscreen_name: str | None = None) -> bool:
        pass

    def rotate_touchscreen(self, rotation: RotationEnum, force_device_name: str | None = None) -> bool:
        pass

    def rotate_screen(self, rotation: RotationEnum, screen: str | None = None) -> bool:
        pass
