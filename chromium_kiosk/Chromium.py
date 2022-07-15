import os
import json
import subprocess
from chromium_kiosk.IBrowser import IBrowser
from chromium_kiosk.tools import find_binary
from chromium_kiosk.config import Config


class Chromium(IBrowser):
    config = None

    def __init__(self, load_extension_path=None):
        """
        Initialize Chromium instance
        """

        executable_path = find_binary([
            'chromium',
            'chromium-browser'
        ])

        if not executable_path:
            raise Exception('Unable to find chromium binary')

        self.executable_path = executable_path
        self.config_path = os.path.expanduser('~/.config/chromium/')
        self.cache_path = os.path.expanduser('~/.cache/chromium/')
        self.load_extension_path = os.path.expanduser(load_extension_path)

        self.arguments = [
            '--noerrdialogs',
            '--disable-infobars',
            '--disable-session-crashed-bubble',
            '--disable-popup-blocking',
            '--disable-breakpad',
            '--disable-cloud-import',
            '--disable-signin-promo',
            '--disable-sync',
            '--fast',
            '--fast-start',
            '--no-first-run'
        ]

        if self.load_extension_path:
            self.arguments.append('--load-extension={}'.format(self.load_extension_path))

        self._update_configuration({
            'translate': {
                'enabled': False  # Disable translate popup
            }
        })

        self._clean_start()

    def set_config(self, config: Config):
        self.config = config

    def _modify_json_file(self, config_path, changes: dict) -> None:
        """
        Modify json file
        :param config_path: 
        :param changes: 
        :return: 
        """
        with open(config_path, 'r') as f:
            config = json.load(f)
            config.update(changes)
            with open(config_path, 'w') as fw:
                json.dump(config, fw)

    def _update_configuration(self, changes: dict) -> None:
        config_paths = [
            'Default/Preferences',
            'Local State'
        ]
        for config_path in config_paths:
            config_path_abs = os.path.join(self.config_path, config_path)
            if os.path.isfile(config_path_abs):
                self._modify_json_file(config_path_abs, changes)

    def _clean_start(self) -> None:
        """
        Run chromium in clean state
        :return: 
        """
        self._update_configuration({
            'exited_cleanly': True,
            'exit_type': 'Normal',
            'profile': {
                'exited_cleanly': True,
                'exit_type': 'Normal'
            }
        })

    def run(self) -> None:
        """
        Start chromium
        :return: 
        """

        if self.config.TOUCHSCREEN:
            self.arguments.append('--touch-events')

        if self.config.FULL_SCREEN:
            self.arguments.append('--kiosk')

        command = [self.executable_path]
        command.extend(self.arguments)

        if self.config.EXTRA_ARGUMENTS:
            command.extend(self.config.EXTRA_ARGUMENTS.split(' '))

        command.append(self.config.HOME_PAGE)

        subprocess.call(command)
