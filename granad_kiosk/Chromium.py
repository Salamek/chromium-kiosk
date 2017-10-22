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

        if not urls:
            urls = []

        self.executable_path = executable_path
        self.config_path = config_path
        self.cache_path = cache_path
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

    def clear_cache(self):
        shutil.rmtree(self.cache_path)

    def set_urls(self, urls):
        self.urls = urls

    def clean_start(self):
        config_paths = [
            'Default/Preferences',
            'Local State'
        ]

    def set_kiosk(self, enabled=True):
        if enabled:
            self.arguments.append('--kiosk')

    def run(self):
        command = [self.executable_path]
        command.extend(self.arguments)
        command.extend(self.urls)
        subprocess.call(command)