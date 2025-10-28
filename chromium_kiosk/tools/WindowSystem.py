from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from chromium_kiosk.enum.RotationEnum import RotationEnum
    from chromium_kiosk.tools.TouchDevice import TouchDevice


class WindowSystem:
    def detect_display(self) -> str | None:
        raise NotImplementedError

    def find_touchscreen_device(self, force_device_name: str | None = None) -> TouchDevice | None:
        raise NotImplementedError

    def detect_primary_screen(self) -> str | None:
        raise NotImplementedError

    def get_screen_rotation(self, screen: str) -> RotationEnum:
        raise NotImplementedError

    def get_touchscreen_rotation(self, touch_device: TouchDevice) -> RotationEnum:
        raise NotImplementedError

    def rotate_display(self, rotation: RotationEnum, screen: str | None = None, force_touchscreen_name: str | None = None) -> bool:
        raise NotImplementedError

    def rotate_touchscreen(self, rotation: RotationEnum, force_device_name: str | None = None) -> bool:
        raise NotImplementedError

    def rotate_screen(self, rotation: RotationEnum, screen: str | None = None) -> bool:
        raise NotImplementedError


