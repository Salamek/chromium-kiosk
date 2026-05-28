#!/bin/sh
xset -dpms      # disable DPMS (Energy Star) features.
xset s off      # disable screen saver
xset s noblank  # don't blank the video device

# Check if xscreensaver is installed, if it is run it

if command -v xscreensaver &> /dev/null
then
    xscreensaver -no-splash & # xscreensaver daemon
fi

unclutter &     # hides your cursor after inactivity

exec openbox-session