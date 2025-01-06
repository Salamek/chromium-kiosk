from typing import Optional

from chromium_kiosk.enum.RotationEnum import RotationEnum
from chromium_kiosk.tools.TouchDevice import TouchDevice
from chromium_kiosk.tools.WindowSystem import WindowSystem


class Wayland(WindowSystem):
    def detect_display(self) -> Optional[str]:
        pass

    def find_touchscreen_device(self, force_device_name: Optional[str] = None) -> Optional[TouchDevice]:
        pass

    def detect_primary_screen(self) -> Optional[str]:
        pass

    def get_screen_rotation(self, screen: str) -> RotationEnum:
        pass

    def get_touchscreen_rotation(self, touch_device: TouchDevice) -> RotationEnum:
        pass

    def rotate_display(self, rotation: RotationEnum, screen: Optional[str] = None,
                       force_touchscreen_name: Optional[str] = None) -> bool:
        pass

    def rotate_touchscreen(self, rotation: RotationEnum, force_device_name: Optional[str] = None) -> bool:
        pass

    def rotate_screen(self, rotation: RotationEnum, screen: Optional[str] = None) -> bool:
        pass