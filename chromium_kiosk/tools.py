import subprocess
import urllib.parse


def create_user(username: str, home: str) -> int:
    return subprocess.call([
        'useradd',
        '--system',
        '--user-group',
        '--shell',
        '/bin/bash',
        '--home-dir',
        home,
        '--create-home',
        username
    ])


def set_user_groups(username: str, groups: list):
    for group in groups:
        command = ['usermod', '-aG', group, username]
        subprocess.call(command)


def inject_parameters_to_url(url: str, parameters: dict) -> str:

    url_parts = list(urllib.parse.urlparse(url))
    query = dict(urllib.parse.parse_qsl(url_parts[4]))
    query.update(parameters)

    url_parts[4] = urllib.parse.urlencode(query)

    return urllib.parse.urlunparse(url_parts)


def get_binary_path(binary_name: str) -> str:
    return subprocess.check_output(['whereis', '-b', binary_name]).decode().split(':')[1].strip()