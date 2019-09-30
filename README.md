# Chromium kiosk

Chromium kiosk is simple package turning your Archlinux or Debian (and alike) based PC/Raspberry into simple web kiosk using chromium.

# Features

* Simple installation and configuration
* Installed from repository
* Restarts whole machine when chromium process crashes/exists

# Installation

## Archlinux
(Use Archlinux ARM for Raspbery install)

Add repository by adding this at end of file /etc/pacman.conf

```
[salamek]
Server = https://arch.salamek.cz/any
SigLevel = Optional
```

and then install by running

```bash
$ pacman -Sy chromium-kiosk
```

# Debian and derivates (WIP)
(For Raspbian i suggest to use Lite relase)

Add repository by running these commands

```bash
$ wget -O - https://apt.salamek.cz/apt/conf/salamek.gpg.key|sudo apt-key add -
$ echo "deb     https://apt.salamek.cz/apt all main" | sudo tee /etc/apt/sources.list.d/salamek.cz.list
```

And then you can install a package python3-gitlab-tools

```bash
$ apt update && apt install python3-chromium-kiosk
```

# Setup

After successful installation you will need to configure chromium-kiosk by editing `/etc/chromium-kiosk/config.yml`, these are the options:

```yml
CLEAN_START: true  # Force chromium to clean start on each boot (That simply means do not show "Restore pages" dialog, you want this to be true in 99% of use cases)
KIOSK: true # Run in kiosk mode, chromium will use whole screen without any way for user to close it, setting this to false is useful for web application debug (you can access chromium Inspect tool and so on) and initial chromium configuration
TOUCHSCREEN: true # Enables support for touchscreen
URLS: # List of urls to load, other urls are loaded as other tabs (on background in this case)
  - `https://github.com/Salamek/chromium-kiosk`
```
