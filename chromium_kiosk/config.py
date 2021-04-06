
class HardCoded(object):
    ADMINS = ['adam.schubert@sg1-game.net']
    USER = 'chromium-kiosk'


class Config(HardCoded):
    DEBUG = True
    CLEAN_START = False
    KIOSK = True
    TOUCHSCREEN = False
    HOME_PAGE = 'http://127.0.0.1/'
    URLS = []  # Deprecated, remove me

    IDLE_TIME = 0
    WHITE_LIST = {
        'ENABLED': False,  # is white list enabled
        'URLS': [],  # List of whitelisted URLs, glob is supported
        'IFRAME_ENABLED': True,  # True to enable all iframes, list of urls to specify enabled iframes
    }

    NAV_BAR = {
        'ENABLED': False,  # is nav bar enabled
        'ENABLED_BUTTONS': ['home', 'reload', 'back', 'forward'],  # Enabled buttons on navbar, order matters
        'HORIZONTAL_POSITION': 'center',  # horizontal position on the screen
        'VERTICAL_POSITION': 'bottom',  # Vertical position on the screen
        'WIDTH': 100,  # Width of a bar in %
    }

    SCREEN_SAVER = {
        'ENABLED': False,  # is nav bar enabled
        'IDLE_TIME': 0,
        'TEXT': 'Touch me'
    }

    VIRTUAL_KEYBOARD = {
        'ENABLED': False
    }

    DISPLAY_ROTATION = 'normal'  # normal|left|right|inverted
    TOUCHSCREEN_ROTATION = 'normal'  # normal|left|right|inverted
    SCREEN_ROTATION = 'normal'  # normal|left|right|inverted


class Testing(Config):
    TESTING = True


class Production(Config):
    DEBUG = False
    CLEAN_START = None  # To be overwritten by a YAML file.
    KIOSK = None  # To be overwritten by a YAML file.
    URLS = None  # To be overwritten by a YAML file.
    TOUCHSCREEN = None  # To be overwritten by a YAML file.
    TOUCHSCREEN_ROTATION = None  # normal|left|right|inverted
    SCREEN_ROTATION = None  # normal|left|right|inverted
    DISPLAY_ROTATION = None # normal|left|right|inverted
