#!/bin/bash

ng build --prod

sed -i 's/url(MaterialIcons-Regular.ttf)/url(chrome-extension:\/\/__MSG_@@extension_id__\/MaterialIcons-Regular.ttf)/g' dist/chromium-kiosk-extension/styles.css
sed -i 's/url(MaterialIcons-Regular.eot)/url(chrome-extension:\/\/__MSG_@@extension_id__\/MaterialIcons-Regular.eot)/g' dist/chromium-kiosk-extension/styles.css
sed -i 's/url(MaterialIcons-Regular.woff2)/url(chrome-extension:\/\/__MSG_@@extension_id__\/MaterialIcons-Regular.woff2)/g' dist/chromium-kiosk-extension/styles.css
sed -i 's/url(MaterialIcons-Regular.woff)/url(chrome-extension:\/\/__MSG_@@extension_id__\/MaterialIcons-Regular.woff)/g' dist/chromium-kiosk-extension/styles.css

# chrome-extension://__MSG_@@extension_id__/ MaterialIcons-Regular.ttf
# eot, woff2
