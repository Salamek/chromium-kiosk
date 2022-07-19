# Chromium kiosk

Chromium kiosk is simple package turning your Linux based PC/Raspberry into simple web kiosk using chromium.

# Features

* Simple installation and configuration
* Installed from repository
* Restarts whole machine when chromium process crashes/exists
* Tested on Archlinux, Archlinux ARM, Debian, Raspbian
* Integrated virtual keyboard (via chromium extension)
* Integrated whitelist (via chromium extension)
* Configurable navbar with back|forward|reload/stop|home buttons
* Redirect to homepage when idle for specified amount of time
* Show screen saver when idle for specified amount of time

# Installation

## Archlinux

Use clean barebone install of Archlinux

(Use Archlinux ARM for Raspberry install)

Add repository by adding this at end of file /etc/pacman.conf

```
[salamek]
Server = https://repository.salamek.cz/arch/pub/$arch
SigLevel = Optional
```

and then install by running

```bash
$ pacman -Sy chromium-kiosk

# Optionally you can install new backend kiosk first browser (https://github.com/Salamek/qiosk) that is used by default insted of chromium when installed
$ pacman -Sy qiosk
```

after that you can reboot your device, you should be welcomed by `chromium-kiosk` welcome page:
```bash
$ reboot
```

# Debian and derivates

Use clean barebone install of Debian/Ubuntu (no DE)

(For Raspbian i suggest to use Lite relase)

Add repository by running these commands

```bash
$ wget -O- https://repository.salamek.cz/deb/salamek.gpg | sudo tee /usr/share/keyrings/salamek-archive-keyring.gpg
$ echo "deb     [signed-by=/usr/share/keyrings/salamek-archive-keyring.gpg] https://repository.salamek.cz/deb/pub all main" | sudo tee /etc/apt/sources.list.d/salamek.cz.list
```

And then you can install a package `chromium-kiosk`

```bash
$ apt update && apt install chromium-kiosk
# Optionally you can install new backend kiosk first browser (https://github.com/Salamek/qiosk) that is used by default insted of chromium when installed
$ apt install qiosk
```

after that you can reboot your device, you should be welcomed by `chromium-kiosk` welcome page:
```bash
$ reboot
```

# Setup

After successful installation you will want to configure `chromium-kiosk` by editing `/etc/chromium-kiosk/config.yml`, these are the options:

```yml
# kiosk option is deprecated, use FULL_SCREEN, KIOSK: true # Run in kiosk mode, chromium will use whole screen without any way for user to close it, setting this to false is useful for web application debug (you can access chromium Inspect tool and so on) and initial chromium configuration
FULL_SCREEN: true # Run in full screen mode, browser will use whole screen without any way for user to close it
TOUCHSCREEN: true # Enables support for touchscreen
HOME_PAGE: 'https://salamek.github.io/chromium-kiosk/'  # Url to load as homepage

# These works only with chromium-kiosk installed
IDLE_TIME: 0 # Seconds, How long must be kiosk idle to redirect to HOME_PAGE, 0=disabled (Works only with chromium-kiosk extension installed)
WHITE_LIST:
  ENABLED': false  # is white list enabled
  URLS': []   # List of whitelisted urls, glob format is supported (eg,: *,google.*/news)
  IFRAME_ENABLED': true  # True to enable all iframes, list of urls to specify enabled iframes

NAV_BAR:
  ENABLED: false # is nav bar enabled
  ENABLED_BUTTONS: ['home', 'reload', 'back', 'forward'] # Enabled buttons on navbar, order matters
  HORIZONTAL_POSITION: 'center' # horizontal position on the screen
  VERTICAL_POSITION: 'bottom' # Vertical position on the screen
  WIDTH: 100 # Width of a bar in %
  HEIGHT: 5 # Height of a bar in % works only for qiosk

VIRTUAL_KEYBOARD:
  ENABLED: false # is virutal keyboard enabled

SCREEN_SAVER:
  ENABLED: false  # is screen saver enabled
  IDLE_TIME: 0  # how long must be a user idle for screensaver to start
  TEXT: 'Touch me'
  
DISPLAY_ROTATION: 'normal' # Rotates display when X server starts options are (normal|left|right|inverted)
#SCREEN_ROTATION: 'normal'  Rotates screen individually (do not rotate touchscreen) when X server starts options are (normal|left|right|inverted), remove DISPLAY_ROTATION for this to work
#TOUCHSCREEN_ROTATION: 'normal'  Rotates touchscreen individually (do not rotate screen) when X server starts options are (normal|left|right|inverted), remove DISPLAY_ROTATION for this to work
#EXTRA_ARGUMENTS: Pass extra arguments to used browser
```

New options when using qiosk a kiosk first browser:

```yml
FULL_SCREEN: true  # Run qiosk in full screen, this replaces KIOSK config option
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
