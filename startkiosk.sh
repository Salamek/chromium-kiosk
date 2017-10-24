#!/bin/sh
xset -dpms      # disable DPMS (Energy Star) features.
xset s off      # disable screen saver
xset s noblank  # don't blank the video device
unclutter &     # hides your cursor after inactivity
#matchbox-window-manager & # starts the WM

#exec chromium --noerrdialogs --disable-infobars --disable-session-crashed-bubble --kiosk --disable-popup-blocking --fast --fast-start --no-first-run http://127.0.0.1:5000?kiosk=1
exec granad-kiosk run --config_prod --log_dir=/var/log