import subprocess
import os
import hashlib
from typing import List, Dict, Callable, Any, Optional, Generic, TypeVar
from chromium_kiosk.config import Config
from chromium_kiosk.tools import find_binary


T = TypeVar("T")


class QioskCommandValue(Generic[T]):

    def __init__(self, value_resolver: Callable[[], T], payload_resolver: Callable[[T], dict], hash_resolver: Optional[Callable[[T], str]] = None):
        self.value = value_resolver()
        self.payload = payload_resolver(self.value)
        self.hash = self._generate_hash(hash_resolver(self.value) if hash_resolver else self.value)

    def _generate_hash(self, payload: str) -> bytes:
        return hashlib.md5(payload.encode()).digest()


    def __repr__(self) -> str:
        return str({'value': self.value, 'payload': self.payload})



class Qiosk:
    config = None

    def __init__(self, config: Config):
        self.config = config
        executable_path = find_binary(['qiosk'])

        if not executable_path:
            raise Exception('Unable to find qiosk binary')

        self.executable_path = executable_path

    def _build_command(self) -> List[str]:
        command = [self.executable_path, self.config.HOME_PAGE]

        if self.config.WINDOW_MODE:
            command.extend(['-m', self.config.WINDOW_MODE])

        if self.config.IDLE_TIME:
            command.extend(['-i', str(self.config.IDLE_TIME)])

        if self.config.WHITE_LIST.get('ENABLED', False):
            for white_list_url in self.config.WHITE_LIST.get('URLS', []):
                command.extend(['-w', white_list_url])

        if self.config.NAV_BAR.get('ENABLED', False):
            command.append('--display-navbar')
            command.extend(['--navbar-horizontal-position', self.config.NAV_BAR.get('HORIZONTAL_POSITION', 'center')])
            command.extend(['--navbar-vertical-position', self.config.NAV_BAR.get('VERTICAL_POSITION', 'bottom')])
            command.extend(['--navbar-width', str(self.config.NAV_BAR.get('WIDTH', 100))])
            command.extend(['--navbar-height', str(self.config.NAV_BAR.get('HEIGHT', 5))])

            enabled_buttons = self.config.NAV_BAR.get('ENABLED_BUTTONS', [])
            if enabled_buttons:
                command.append('--navbar-enable-buttons={}'.format(','.join(enabled_buttons).lower()))

            if self.config.NAV_BAR.get('UNDERLAY', False):
                command.append('--underlay-navbar')

        command.extend(['--profile-name', self.config.PROFILE_NAME])

        for allowed_feature in self.config.ALLOWED_FEATURES:
            command.extend(['-a', allowed_feature])

        if self.config.ADDRESS_BAR.get('ENABLED', False):
            command.append('--display-addressbar')

        if self.config.SCROLL_BARS.get('ENABLED', False):
            command.append('--display-scroll-bars')

        if not self.config.CURSOR.get('ENABLED', True):
            command.append('--hide-cursor')

        return command

    def _build_env(self) -> Dict[str, str]:
        my_env = os.environ.copy()

        my_env.update({k: str(v) for k, v in self.config.EXTRA_ENV_VARS.items()})

        if self.config.REMOTE_DEBUGGING:
            my_env['QTWEBENGINE_REMOTE_DEBUGGING'] = str(self.config.REMOTE_DEBUGGING)

        if self.config.EXTRA_ARGUMENTS:
            my_env['QTWEBENGINE_CHROMIUM_FLAGS'] = self.config.EXTRA_ARGUMENTS

        if self.config.VIRTUAL_KEYBOARD.get('ENABLED', False):
            my_env['QT_IM_MODULE'] = 'qtvirtualkeyboard'

        return my_env

    @staticmethod
    def resolve_command_mappings_config(config: Config) -> Dict[str, QioskCommandValue]:
        def white_list_value_resolver() -> List[str]:
            if not config.WHITE_LIST.get('ENABLED', False):
                return []

            return config.WHITE_LIST.get('URLS', [])

        def white_list_hash_resolver(value: List[str]) -> str:
            return ''.join(value)

        def permissions_value_resolver() -> List[str]:
            return config.WHITE_LIST.get('ALLOWED_FEATURES', [])

        def permissions_hash_resolver(value: List[str]) -> str:
            return ''.join(value)

        return {
            'setHomePage': QioskCommandValue[str](
                value_resolver=lambda: config.HOME_PAGE,
                payload_resolver=lambda value: {'homePageUrl': value}
            ),
            'setUrl': QioskCommandValue[str](
                value_resolver=lambda: config.HOME_PAGE,
                payload_resolver=lambda value: {'url': value}
            ),
            'setWindowMode': QioskCommandValue[str](
                value_resolver=lambda: config.WINDOW_MODE,
                payload_resolver=lambda value: {'windowMode': value}
            ),
            'setIdleTime': QioskCommandValue[int](
                value_resolver=lambda: config.IDLE_TIME,
                hash_resolver=lambda value: str(value),
                payload_resolver=lambda value: {'idleTime': value}
            ),
            'setWhiteList':  QioskCommandValue[List[str]](
                value_resolver=white_list_value_resolver,
                hash_resolver=white_list_hash_resolver,
                payload_resolver=lambda value: {'whitelist': value}
            ),
            'setPermissions': QioskCommandValue[List[str]](
                value_resolver=permissions_value_resolver,
                hash_resolver=permissions_hash_resolver,
                payload_resolver=lambda value: {'permissions': value}
            ),
            'setNavbarVerticalPosition': QioskCommandValue[str](
                value_resolver=lambda: config.NAV_BAR.get('VERTICAL_POSITION', 'bottom'),
                payload_resolver=lambda value: {'navbarVerticalPosition': value}
            ),
            'setNavbarHorizontalPosition': QioskCommandValue[str](
                value_resolver=lambda: config.NAV_BAR.get('HORIZONTAL_POSITION', 'center'),
                payload_resolver=lambda value: {'navbarHorizontalPosition': value}
            ),
            'setNavbarWidth': QioskCommandValue[int](
                value_resolver=lambda: config.NAV_BAR.get('WIDTH', 100),
                hash_resolver=lambda value: str(value),
                payload_resolver=lambda value: {'navbarWidth': value}
            ),
            'setNavbarHeight': QioskCommandValue[int](
                value_resolver=lambda: config.NAV_BAR.get('HEIGHT', 5),
                hash_resolver=lambda value: str(value),
                payload_resolver=lambda value: {'navbarHeight': value}
            ),
            'setDisplayAddressBar': QioskCommandValue[bool](
                value_resolver=lambda: config.NAV_BAR.get('ADDRESS_BAR', False),
                hash_resolver=lambda value: str(value),
                payload_resolver=lambda value: {'displayAddressBar': value}
            ),
            'setDisplayNavBar': QioskCommandValue[bool](
                value_resolver=lambda: config.NAV_BAR.get('ENABLED', False),
                hash_resolver=lambda value: str(value),
                payload_resolver=lambda value: {'displayNavBar': value}
            ),
            'setUnderlayNavBar': QioskCommandValue[bool](
                value_resolver=lambda: config.NAV_BAR.get('UNDERLAY', False),
                hash_resolver=lambda value: str(value),
                payload_resolver=lambda value: {'underlayNavBar': value}
            ),
        }

    @staticmethod
    def diff_command_mappings_config_value(old: Dict[str, QioskCommandValue], new: Dict[str, QioskCommandValue]) -> Dict[str, QioskCommandValue]:
        """
        Diff values of QioskCommandValue
        :param old:
        :param new:
        :return:
        """

        diffs = {}
        for key, value in old.items():
            if key in new:
                # We ignore removed config values
                new_value = new.get(key)
                if new_value.hash != value.hash:
                    diffs[key] = new_value

        # Any new keys in new?
        new_keys = new.keys() - old.keys()
        for new_key in new_keys:
            diffs[new_key] = new.get(new_key)

        return diffs

    def run(self) -> None:
        """
        Start browser
        :return:
        """

        subprocess.call(self._build_command(), env=self._build_env())
