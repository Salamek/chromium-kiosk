import os
import json
import shutil
import subprocess
from typing import Union


class Chromium(object):
    def __init__(self,
                 config_path='~/.config/chromium/',
                 cache_path='~/.cache/chromium/',
                 urls=None,
                 load_extension_path=None
                 ):
        """
        Initialize Chromium instance
        :param config_path: path to chromium config dir
        :param cache_path: path to chromium config cache
        """

        executable_path = self._find_chromium()

        if not executable_path:
            raise Exception('Unable to find chromium binary')

        self.executable_path = executable_path
        self.config_path = os.path.expanduser(config_path)
        self.cache_path = os.path.expanduser(cache_path)
        self.load_extension_path = os.path.expanduser(load_extension_path)
        if not urls:
            urls = []

        self.urls = urls
        self.arguments = [
            '--noerrdialogs',
            '--disable-infobars',
            '--disable-session-crashed-bubble',
            '--disable-popup-blocking',
            '--disable-translate',
            '--disable-features=TranslateUI',
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

    def _find_chromium(self) -> Union[str, None]:
        """
        Find chromium binary
        :return: 
        """
        names = [
            'chromium',
            'chromium-browser'
        ]

        for name in names:
            found = shutil.which(name)
            if found:
                return found

    def clear_cache(self) -> None:
        """
        Clears chromium cache
        :return: 
        """
        shutil.rmtree(self.cache_path)

    def set_urls(self, urls):
        """
        Sets list of urls to open
        :param urls: 
        :return: 
        """
        self.urls = urls

    def _modify_config(self, config_path, changes: dict) -> None:
        """
        Modify chromium config
        :param config_path: 
        :param changes: 
        :return: 
        """
        with open(config_path, 'r') as f:
            config = json.load(f)
            config.update(changes)
            with open(config_path, 'w') as fw:
                json.dump(config, fw)

    def clean_start(self) -> None:
        """
        Run chromium in clean state
        :return: 
        """
        config_paths = [
            'Default/Preferences',
            'Local State'
        ]
        for config_path in config_paths:
            config_path_abs = os.path.join(self.config_path, config_path)
            if os.path.isfile(config_path_abs):
                self._modify_config(config_path_abs, {
                    'exited_cleanly': True,
                    'exit_type': 'Normal',
                    'profile': {
                        'exited_cleanly': True,
                        'exit_type': 'Normal'
                    }
                })

    def set_kiosk(self, enabled: bool=True) -> None:
        """
        Set chromium to run in kiosk mode
        :param enabled: 
        :return: 
        """
        if enabled:
            self.arguments.append('--kiosk')

    def set_touchscreen(self, enabled: bool=True) -> None:
        """
        Sets touchscreen support
        :param enabled:
        :return:
        """
        if enabled:
            self.arguments.append('--touch-events')

    def run(self) -> None:
        """
        Start chromium
        :return: 
        """
        command = [self.executable_path]
        command.extend(self.arguments)
        command.extend(self.urls)

        subprocess.call(command)