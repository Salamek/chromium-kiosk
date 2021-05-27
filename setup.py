#!/usr/bin/env python
import os
from glob import glob
import sys

from typing import List, Union
from setuptools import setup, find_packages

sys_conf_dir = os.getenv("SYSCONFDIR", "/etc")
data_dir = os.getenv("DATADIR", "/usr/share")
lib_dir = os.getenv("LIBDIR", "/usr/lib")


def get_requirements(filename: str) -> list:
    return open(os.path.join(filename)).read().splitlines()


def package_files(directory: str) -> List[str]:
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


classes = """
    Development Status :: 4 - Beta
    Intended Audience :: Developers
    Programming Language :: Python
    Programming Language :: Python :: 2
    Programming Language :: Python :: 2.7
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3.3
    Programming Language :: Python :: 3.4
    Programming Language :: Python :: 3.5
    Programming Language :: Python :: 3.6
    Programming Language :: Python :: Implementation :: CPython
    Programming Language :: Python :: Implementation :: PyPy
    Operating System :: OS Independent
"""
classifiers = [s.strip() for s in classes.split('\n') if s]


install_requires = get_requirements('requirements.txt')
if sys.version_info < (3, 0):
    install_requires.append('futures')


extra_files = [
]

setup(
    name='chromium-kiosk',
    version='0.5.6',
    description='Chromium Kiosk',
    long_description=open('README.md').read(),
    author='Adam Schubert',
    author_email='adam.schubert@sg1-game.net',
    url='https://github.com/Salamek/chromium-kiosk',
    license='GPL-3.0',
    classifiers=classifiers,
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=install_requires,
    test_suite="tests",
    tests_require=install_requires,
    package_data={'chromium-kiosk': extra_files},
    entry_points={
        'console_scripts': [
            'chromium-kiosk = chromium_kiosk.__main__:main',
        ],
    },
    data_files=[
        (os.path.join(sys_conf_dir, 'systemd', 'system', 'getty@tty1.service.d'), [
            'etc/systemd/system/getty@tty1.service.d/override.conf'
        ]),
        (os.path.join(sys_conf_dir, 'chromium-kiosk'), [
            'etc/chromium-kiosk/config.yml'
        ]),
        (os.path.join(lib_dir, 'systemd', 'system'), [
            'lib/systemd/system/chromium-kiosk_configwatcher.service',
        ]),
        (
            os.path.join(data_dir, 'chromium-kiosk/chromium-kiosk-extension'),
            [file for file in glob('chromium-kiosk-extension/dist/chromium-kiosk-extension/*', recursive=True) if not os.path.isdir(file)]
        ),
        (
            os.path.join(data_dir, 'chromium-kiosk/chromium-kiosk-extension/assets'),
            [file for file in glob('chromium-kiosk-extension/dist/chromium-kiosk-extension/assets/*', recursive=True) if not os.path.isdir(file)]
        ),
        (
            os.path.join(data_dir, 'chromium-kiosk/chromium-kiosk-extension/assets/bar-controls'),
            [file for file in glob('chromium-kiosk-extension/dist/chromium-kiosk-extension/assets/bar-controls/*', recursive=True) if
             not os.path.isdir(file)]
        ),
    ]
)
