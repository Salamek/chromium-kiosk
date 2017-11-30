#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import sys
import subprocess
from distutils.version import LooseVersion, StrictVersion


class VersionModifier(object):
    version_file = None

    def __init__(self):
        base = os.path.abspath(os.path.dirname(__file__))
        self.version_file_path = os.path.join(base, "granad_kiosk/__init__.py")
        with open(self.version_file_path, 'r') as init_f:
            self.version_file = init_f.read()

    def get_current_version(self):
        version = re.compile(r'VERSION\s*=\s*\((.*?)\)')
        return StrictVersion('.'.join(version.match(self.version_file).group(1).split(',')).replace(' ', ''))

    def set_current_version(self, version):
        file_content = re.sub(r'VERSION\s*=\s*\((.*?)\)', r'VERSION = ({})'.format(', '.join(str(x) for x in version)), self.version_file)
        with open(self.version_file_path, 'w') as init_f:
            init_f.write(file_content)

    def tag(self, version_string):
        subprocess.call(['git', 'add', 'granad_kiosk/__init__.py'])
        subprocess.call(['git', 'add', 'archlinux/PKGBUILD'])
        subprocess.call(['git', 'commit', '-m', "New version {}".format(version_string)])
        subprocess.call(['git', 'tag', '-a', version_string, '-m', "New version {}".format(version_string)])
        subprocess.call(['git', 'push'])
        subprocess.call(['git', 'push', '--tags'])

    def set_version(self, version_string):
        current_version = self.get_current_version()
        version = StrictVersion(version_string)
        if version < current_version:
            raise Exception('Requested version {} is lower than current version {}'.format(version_string, current_version))

        self.set_current_version(version.version)

        # Set version to PKGBUILD
        base = os.path.abspath(os.path.dirname(__file__))
        pkg_build_path = os.path.join(base, "archlinux/PKGBUILD")
        with open(pkg_build_path, 'r') as init_f:
            file_content = init_f.read()
            new_file_content = re.sub(r'pkgver\s*=\s*(.*)', r'pkgver={}'.format(version), file_content)
            with open(pkg_build_path, 'w') as write_f:
                write_f.write(new_file_content)

        self.tag(version_string)


version_modifier = VersionModifier()

if len(sys.argv) == 2:
    version_modifier.set_version(sys.argv[1])
else:
    print(version_modifier.get_current_version())
