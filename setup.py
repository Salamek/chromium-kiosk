import os

from setuptools import setup

sys_conf_dir = os.getenv("SYSCONFDIR", "/etc")
usr_lib_dir = os.getenv("LIBDIR", "/usr/lib")
var_lib_dir = os.getenv("VARLIBDIR", "/var/lib")


setup(

    data_files=[
        (os.path.join(sys_conf_dir, "chromium-kiosk"), [  # noqa: PTH118
            "etc/chromium-kiosk/config.yml",
        ]),
        (os.path.join(usr_lib_dir, "systemd", "system", "getty@tty1.service.d"), [  # noqa: PTH118
            "usr/lib/systemd/system/getty@tty1.service.d/override.conf",
        ]),
        (os.path.join(usr_lib_dir, "systemd", "system"), [  # noqa: PTH118
            "usr/lib/systemd/system/chromium-kiosk_configwatcher.service",
        ]),
        (os.path.join(usr_lib_dir, "sysusers.d"), [  # noqa: PTH118
            "usr/lib/sysusers.d/chromium-kiosk.conf",
        ]),
        (os.path.join(usr_lib_dir, "tmpfiles.d"), [  # noqa: PTH118
            "usr/lib/tmpfiles.d/chromium-kiosk.conf",
        ]),
        (os.path.join(var_lib_dir, "chromium-kiosk"), [  # noqa: PTH118
            "var/lib/chromium-kiosk/.bash_profile",
            "var/lib/chromium-kiosk/.hushlogin",
            "var/lib/chromium-kiosk/.xinitrc",
        ]),
    ],
)
