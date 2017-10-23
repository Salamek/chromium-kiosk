import os
import json
import shutil
import subprocess


class Chromium(object):
    def __init__(self,
                 executable_path='chromium',
                 config_path='~/.config/chromium/',
                 cache_path='~/.cache/chromium/',
                 urls=None
                 ):
        """
        Initialize Chromium instance
        :param executable_path: path to chromium binary
        :param config_path: path to chromium config dir
        :param cache_path: path to chromium config cache
        """

        self.executable_path = executable_path
        self.config_path = config_path
        self.cache_path = cache_path
        if not urls:
            urls = []

        self.urls = urls
        self.arguments = [
            '--noerrdialogs',
            '--disable-infobars',
            '--disable-session-crashed-bubble',
            '--disable-popup-blocking',
            '--fast',
            '--fast-start',
            '--no-first-run'
        ]

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
        with open(config_path, 'rw') as f:
            config = json.load(f)
            config.update(changes)
            json.dump(config, f)

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
            self._modify_config(os.path.join(self.config_path, config_path), {
                'exited_cleanly': True,
                'exit_type': 'Normal'
            })

    def set_kiosk(self, enabled: bool=True) -> None:
        """
        Set chromium to run in kiosk mode
        :param enabled: 
        :return: 
        """
        if enabled:
            self.arguments.append('--kiosk')

    def run(self) -> None:
        """
        Start chromium
        :return: 
        """
        command = [self.executable_path]
        command.extend(self.arguments)
        command.append(self.urls)
        subprocess.call(command)