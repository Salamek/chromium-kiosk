from typing import TypedDict


class WhiteList(TypedDict):
    ENABLED: bool
    URLS: list[str]
    IFRAME_ENABLED: bool


class NavBar(TypedDict):
    ENABLED: bool
    ENABLED_BUTTONS: list[str]
    HORIZONTAL_POSITION: str
    VERTICAL_POSITION: str
    WIDTH: int
    HEIGHT: int
    UNDERLAY: bool

class VirtualKeyboard(TypedDict):
    ENABLED: bool


class HardCoded:
    ADMINS = ["adam.schubert@sg1-game.net"]
    USER = "chromium-kiosk"


class Config(HardCoded):
    DEBUG = True
    FULL_SCREEN = None  # Deprecated, do not use # @TODO remove in next minor version
    WINDOW_MODE = "fullscreen"  # one of hidden|automaticvisibility|windowed|minimized|maximized|fullscreen
    TOUCHSCREEN = None  # None=autodetect, set to device name to force
    HOME_PAGE: str = "http://127.0.0.1/"

    IDLE_TIME = 0
    WHITE_LIST: WhiteList = {
        "ENABLED": False,  # is white list enabled
        "URLS": [],  # List of whitelisted URLs, glob is supported
        "IFRAME_ENABLED": True,  # True to enable all iframes, list of urls to specify enabled iframes
    }

    NAV_BAR: NavBar = {
        "ENABLED": False,  # is nav bar enabled
        "ENABLED_BUTTONS": ["home", "reload", "back", "forward"],  # Enabled buttons on navbar, order matters
        "HORIZONTAL_POSITION": "center",  # horizontal position on the screen
        "VERTICAL_POSITION": "bottom",  # Vertical position on the screen
        "WIDTH": 100,  # Width of a bar in %
        "HEIGHT": 5,  # Width of a bar in %
        "UNDERLAY": False,  # If set to True, the navbar will be displayed under the web view
    }

    VIRTUAL_KEYBOARD: VirtualKeyboard = {
        "ENABLED": False,
    }

    DISPLAY_ROTATION = "normal"  # normal|left|right|inverted
    TOUCHSCREEN_ROTATION = "normal"  # normal|left|right|inverted
    SCREEN_ROTATION = "normal"  # normal|left|right|inverted

    ALLOWED_FEATURES: list[str] = [  # Set enabled features
        #'desktop-audio-video-capture',
        #'desktop-video-capture',
        #'geolocation',
        #'invalid-certificate',
        #'media-audio-capture',
        #'media-audio-video-capture',
        #'media-video-capture',
        #'mouse-lock',
        #'notifications'
    ]

    REMOTE_DEBUGGING = None  # Set to port number to enable

    EXTRA_ARGUMENTS = None  # Pass extra arguments to used browser

    EXTRA_ENV_VARS: dict[str, str] = {}

    PROFILE_NAME = "default"  # Name of profile used by browser, default is name of default off-the-record profile, use custom name to persist cookies and other data

    ADDRESS_BAR = {
        "ENABLED": False,
    }

    SCROLL_BARS = {
        "ENABLED": False,
    }

    CURSOR = {
        "ENABLED": True,
    }



class Testing(Config):
    TESTING = True


class Production(Config):
    DEBUG = False
    CLEAN_START = None  # To be overwritten by a YAML file.
    TOUCHSCREEN = None  # To be overwritten by a YAML file.
