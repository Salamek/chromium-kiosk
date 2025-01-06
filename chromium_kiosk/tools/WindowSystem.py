from typing import Optional
from chromium_kiosk.enum.RotationEnum import RotationEnum
from chromium_kiosk.tools.TouchDevice import TouchDevice


class WindowSystem:
    def detect_display(self) -> Optional[str]:
        raise NotImplementedError

    def find_touchscreen_device(self, force_device_name: Optional[str] = None) -> Optional[TouchDevice]:
        raise NotImplementedError

    def detect_primary_screen(self) -> Optional[str]:
        raise NotImplementedError

    def get_screen_rotation(self, screen: str) -> RotationEnum:
        raise NotImplementedError

    def get_touchscreen_rotation(self, touch_device: TouchDevice) -> RotationEnum:
        raise NotImplementedError

    def rotate_display(self, rotation: RotationEnum, screen: Optional[str] = None, force_touchscreen_name: Optional[str] = None) -> bool:
        raise NotImplementedError

    def rotate_touchscreen(self, rotation: RotationEnum, force_device_name: Optional[str] = None) -> bool:
        raise NotImplementedError

    def rotate_screen(self, rotation: RotationEnum, screen: Optional[str] = None) -> bool:
        raise NotImplementedError


