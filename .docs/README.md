# Chromium Kiosk

Chromium kiosk is simple package turning your Linux based PC/Raspberry into simple web kiosk using chromium.

Currently `chromium-kiosk` supports these backends:

* [qiosk](https://github.com/Salamek/qiosk) A kiosk first browser specially made for `chromium-kiosk` written in QT5/QT6



## Content
- [Installation](#installation)
  - [Debian](#debian)
  - [Archlinux](#archlinux)
  - [Raspberry Pi](#raspberry-pi)
- [Configuration](#configuration)
- [Tips and tricks](#tips-and-tricks)
  - [Screensaver](#screensaver)
  - [Periodic reboot](#periodic-reboot)


## Installation

Chromium kiosk can be installed on multiple Linux based distributions, officially supported are Debian 11 and Archlinux other distributions based on Debian may work too.

- **Debian**
- **Archlinux**
- **Raspberry Pi**

### Debian

For Debian there are prepared DEB packages in my repository:

1) Make sure that your system is up-to-date

```bash
apt update && apt upgrade
```

2) Install required dependencies

```bash
apt install wget
```

3) Add GPG key for my repository

```bash
wget -O- https://repository.salamek.cz/deb/salamek.gpg | tee /usr/share/keyrings/salamek-archive-keyring.gpg > /dev/null
```

4) Add repository

```bash
echo "deb     [signed-by=/usr/share/keyrings/salamek-archive-keyring.gpg] https://repository.salamek.cz/deb/pub all main" | tee /etc/apt/sources.list.d/salamek.cz.list
```

5) Install chromium-kiosk

```bash
apt install chromium-kiosk
```

WARNING: Current debian stable `libqt5webengine5` has broken integrated PDF reader, if you need to use PDFs in your kiosk, you will need to add debian backports repo and install `qt6-qiosk` (QT6 port of qiosk):

1) Add backports repository

```bash
echo "deb http://deb.debian.org/debian bullseye-backports main contrib non-free" | tee /etc/apt/sources.list.d/backports.list
```

2) Install QT6 version of qiosk
```
apt install qt6-qiosk
```


### Archlinux

For Archlinux there are prepared packages in my repository:

1) Make sure that your system is up-to-date

```bash
pacman -Syu
```

2) Add repository by adding this into your `/etc/pacman.conf`

```ini
[salamek]
Server = https://repository.salamek.cz/arch/pub/$arch
SigLevel = Optional
```

5) Install chromium-kiosk

```bash
pacman -Sy chromium-kiosk
```

### Raspberry Pi

Installation on Raspberry Pi is a bit different since we use Debian arm64 for Raspberry installs:
(Official Raspbian images/repos are missing some `qiosk` dependencies...)

1) Download required image (Debian 11) from https://raspi.debian.net/tested-images/ for you Raspberry Pi version

```bash
# Example download for RPI3B+ (Please use URL you have obtained from link above, this one my not work)
wget https://raspi.debian.net/tested/20220121_raspi_3_bullseye.img.xz
```

2) Extract image to SD-CARD (You can also use GUI apps like disks-tool, Etcher, rufus, etc...)

```bash
xzcat 20220121_raspi_3_bullseye.img.xz | dd of=/dev/sdX status=progress
sync
```

3) After successful boot of your Raspberry Pi, you can continue with installation by following steps for [Debian](#debian)


## Configuration

**Content of configuration file is self-explanatory**

 ```yaml
FULL_SCREEN: true # Run in full screen mode, browser will use whole screen without any way for user to close it
TOUCHSCREEN: true # Enables support for touchscreen
HOME_PAGE: 'https://salamek.github.io/chromium-kiosk/'  # Url to load as homepage

IDLE_TIME: 0 # Seconds, How log must be kiosk idle to redirect to HOME_PAGE, 0=disabled
WHITE_LIST:
  ENABLED: false  # is white list enabled
  URLS: []   # List of whitelisted urls, glob format is supported (eg,: *,google.*/news)
  IFRAME_ENABLED: true  # True to enable all iframes, list of urls to specify enabled iframes

NAV_BAR:
  ENABLED: false # is nav bar enabled
  ENABLED_BUTTONS: ['home', 'reload', 'back', 'forward'] # Enabled buttons on navbar, order matters
  HORIZONTAL_POSITION: 'center' # horizontal position on the screen
  VERTICAL_POSITION: 'bottom' # Vertical position on the screen
  WIDTH: 100 # Width of a bar in %
  HEIGHT: 5 # Height of a bar in %

VIRTUAL_KEYBOARD:
  ENABLED: false

DISPLAY_ROTATION: 'normal' # normal|left|right|inverted
#SCREEN_ROTATION: 'normal'  #Rotates screen individually (do not rotate touchscreen) when X server starts options are (normal|left|right|inverted), remove DISPLAY_ROTATION for this to work
#TOUCHSCREEN_ROTATION: 'normal'  #Rotates touchscreen individually (do not rotate screen) when X server starts options are (normal|left|right|inverted), remove DISPLAY_ROTATION for this to work
#EXTRA_ARGUMENTS: # Pass extra arguments to used browser, in case of qiosk thse arguments are passed to chromium using QTWEBENGINE_CHROMIUM_FLAGS

#ADDRESS_BAR:
#  ENABLED: false

# Allowed features in browser
# Uncomment feature you want to enable
#ALLOWED_FEATURES:
#  - desktop-audio-video-capture  # Allows recording desktop audio and video
#  - desktop-video-capture  # Allows recording desktop video
#  - geolocation  # Allows geolocation
#  - invalid-certificate  # Ignores invalid certificate
#  - media-audio-capture  # Allows recording audio from capture device (MIC)
#  - media-audio-video-capture  # Allows recording audio and video from capture device (Camera w/ MIC)
#  - media-video-capture  # Allows recording vide from capture device (Camera)
#  - mouse-lock  # Allows locking mouse inside browser full screen window
#  - notifications  # Allows notifications to be accepted from website

#REMOTE_DEBUGGING:  # Set to port number to enable available only when using qiosk browser
```

# Tips and tricks

## Screensaver

Since version 1.1.0 `chromium-kiosk` no longer manages screensaver or installs xscreensaver dependencies for you, but it is still compatible with xscreensaver, you can install and configure xscreensaver in a standart way:

### Installation
```bash
# For standart xscreensaver install
apt get install xscreensaver

# If you want to use chromium-kiosk text screensaver as before, you will need to install `xscreensaver-bouncing-text` package
apt get install xscreensaver-bouncing-text
```

### Configuration
For xscreensaver configuration we use standart xscreensaver configuration file in users home folder a ~/.xscreensaver:

```bash
nano /home/chromium-kiosk/.xscreensaver
```
and insert this configuration:

```
timeout: 0:00:10
cycle: 0
lock: False
visualID: default
dpmsEnabled: False
splash: False
fade: True
mode: one
selected: 0
programs: \
  GL: 				xscreensaver-bouncing-text --text='Touch me please'			    \n\

```

`timeout` is time to wait before displaying the screensaver in format H:mm:ss. to change the text, change text inside `'Touch me please'` to desired value. You can also configure screensaver from standart xscreensaver GUI config (xscreensaver-demo)

## Periodic reboot
Sometines (when web page you are displaying has memory leak) only way how to keep your kiosk working is periodically restart the kiosk browser or even whole machine, here you can see how to do it:

We will use CRON, create file in `/etc/cron.d/chromium-kiosk`

```bash
nano /etc/cron.d/chromium-kiosk
```
With this content for browser restart each midnight:

```
0 0 * * * root /usr/bin/killall -u chromium-kiosk
```

or with this content for machine restart each midnight:
```
0 0 * * * root /usr/sbin/shutdown -r
```










