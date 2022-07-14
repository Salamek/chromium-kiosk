
class HardCoded(object):
    ADMINS = ['adam.schubert@sg1-game.net']
    USER = 'chromium-kiosk'


class Config(HardCoded):
    DEBUG = True
    KIOSK = True  #@TODO Deprecated in qiosk replaced by FULLSCREEN
    FULL_SCREEN = True
    TOUCHSCREEN = False
    HOME_PAGE = 'http://127.0.0.1/'

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
        'ENABLED': False,  # is screen saver controlled by chromium kiosk
        'IDLE_TIME': 0,
        'TEXT': 'Touch me'
    }

    VIRTUAL_KEYBOARD = {  #@TODO Deprecated, there is no reason to have this option for qiosk, VIRTUAL_KEYBOARD is enabled at all times
        'ENABLED': False
    }

    DISPLAY_ROTATION = 'normal'  # normal|left|right|inverted
    TOUCHSCREEN_ROTATION = 'normal'  # normal|left|right|inverted
    SCREEN_ROTATION = 'normal'  # normal|left|right|inverted

    ALLOWED_FEATURES = [  # Set enabled features, available only when using qiosk browser
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

    REMOTE_DEBUGGING = None  # Set to port number to enable available only when using qiosk browser

    EXTRA_ARGUMENTS = None  # Pass extra arguments to used browser


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
