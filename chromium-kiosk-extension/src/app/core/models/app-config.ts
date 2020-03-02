
export class AppNavbarConfig {
  enabled: boolean; // Is navbar enabled
  enabledButtons: string[]; // list of enabled buttons, empty=all, Order matters
  horizontalPosition: string; // Horizontal position ['left|center|right']
  verticalPosition: string; // Vertical position ['bottom|top']
  width: number; // Width of bar in %, default is 100%
}

export class AppVirtualKeyboardConfig {
  enabled: boolean; // Is virtual keyboard enabled
}

export class AppWhiteListConfig {
  enabled: boolean; // Is virtual keyboard enabled
  urls: string[]; // List of whitelisted urls
  iframeEnabled: string[] | boolean; // Are page iframe enabled ? true|['url', 'url2']|false
}

export class AppScreenSaverConfig {
  enabled: boolean;
  idleTime: number; // How long can user be idle before screensaver starts
  text: string;
}

export class AppConfig {
  homePage: string; // Homepage
  idleTime: number; // How long can user be idle before redirect to homepage in seconds, 0 for infinite
  screenSaver: AppScreenSaverConfig;
  whiteList: AppWhiteListConfig; // Whitelist config
  navBar: AppNavbarConfig; // Navbar settings
  virtualKeyboard: AppVirtualKeyboardConfig; // virtual keyboard settings
}
