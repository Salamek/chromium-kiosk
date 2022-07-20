import subprocess
import os
from chromium_kiosk.IBrowser import IBrowser
from chromium_kiosk.config import Config
from chromium_kiosk.tools import find_binary


class Qiosk(IBrowser):
    config = None

    def __init__(self):
        executable_path = find_binary(['qiosk'])

        if not executable_path:
            raise Exception('Unable to find qiosk binary')

        self.executable_path = executable_path

    def set_config(self, config: Config):
        self.config = config

    def run(self) -> None:
        """
        Start browser
        :return:
        """
        command = [self.executable_path, self.config.HOME_PAGE]

        if self.config.FULL_SCREEN:
            command.append('-f')

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

        for allowed_feature in self.config.ALLOWED_FEATURES:
            command.extend(['-a', allowed_feature])

        if self.config.ADDRESS_BAR.get('ENABLED', False):
            command.append('--display-addressbar')

        my_env = os.environ.copy()

        if self.config.REMOTE_DEBUGGING:
            my_env['QTWEBENGINE_REMOTE_DEBUGGING'] = self.config.REMOTE_DEBUGGING

        if self.config.EXTRA_ARGUMENTS:
            my_env['QTWEBENGINE_CHROMIUM_FLAGS'] = self.config.EXTRA_ARGUMENTS

        if self.config.VIRTUAL_KEYBOARD.get('ENABLED', False):
            my_env['QT_IM_MODULE'] = 'qtvirtualkeyboard'

        subprocess.call(command, env=my_env)
