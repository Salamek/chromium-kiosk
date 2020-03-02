# Chromium kiosk

Chromium kiosk is simple package turning your Linux based PC/Raspberry into simple web kiosk using chromium.

# Features

* Simple installation and configuration
* Installed from repository
* Restarts whole machine when chromium process crashes/exists
* Tested on Archlinux, Archlinux ARM, Debian, Raspbian

# Installation

## Archlinux
(Use Archlinux ARM for Raspberry install)

Add repository by adding this at end of file /etc/pacman.conf

```
[salamek]
Server = https://repository.salamek.cz/arch/pub/any
SigLevel = Optional
```

and then install by running

```bash
$ pacman -Sy chromium-kiosk
```

after that you can reboot your device, you should be welcomed by `chromium-kiosk` welcome page:
```bash
$ reboot
```

# Debian and derivates
(For Raspbian i suggest to use Lite relase)

Add repository by running these commands

```bash
$ wget -O - https://repository.salamek.cz/deb/salamek.gpg.key|sudo apt-key add -
$ echo "deb     https://repository.salamek.cz/deb/pub all main" | sudo tee /etc/apt/sources.list.d/salamek.cz.list
```

And then you can install a package `chromium-kiosk`

```bash
$ apt update && apt install chromium-kiosk
```

after that you can reboot your device, you should be welcomed by `chromium-kiosk` welcome page:
```bash
$ reboot
```

# Setup

After successful installation you will want to configure `chromium-kiosk` by editing `/etc/chromium-kiosk/config.yml`, these are the options:

```yml
CLEAN_START: true  # Force chromium to clean start on each boot (That simply means do not show "Restore pages" dialog, you want this to be true in 99% of use cases)
KIOSK: true # Run in kiosk mode, chromium will use whole screen without any way for user to close it, setting this to false is useful for web application debug (you can access chromium Inspect tool and so on) and initial chromium configuration
TOUCHSCREEN: true # Enables support for touchscreen
URLS: # List of urls to load, other urls are loaded as other tabs (on background in this case)
  - `https://github.com/Salamek/chromium-kiosk`
```
