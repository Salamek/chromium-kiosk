
class HardCoded(object):
    ADMINS = ['adam.schubert@sg1-game.net']
    USER = 'granad-kiosk'
    HOSTNAME = 'granad-kiosk'


class Config(HardCoded):
    DEBUG = True
    CLEAN_START = False
    KIOSK = True
    URLS = [
        'http://127.0.0.1/?kiosk=1'
    ]


class Testing(Config):
    TESTING = True


class Production(Config):
    DEBUG = False
    CLEAN_START = None  # To be overwritten by a YAML file.
    KIOSK = None  # To be overwritten by a YAML file.
    URLS = None  # To be overwritten by a YAML file.
