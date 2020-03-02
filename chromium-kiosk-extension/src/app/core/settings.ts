import {
  AppConfig,
  AppNavbarConfig,
  AppVirtualKeyboardConfig,
  AppWhiteListConfig,
  AppScreenSaverConfig
} from '@app/core/models/app-config';

export class DefaultSettings extends AppConfig {
  homePage: string = 'https://salamek.github.io/chromium-kiosk/';
  idleTime: number = 0;
  whiteList: AppWhiteListConfig = <AppWhiteListConfig>{
    enabled: false, // Is virtual keyboard enabled
    urls: [], // List of whitelisted urls
    iframeEnabled: false // Are page iframe enabled ? true|['url', 'url2']|false
  };
  navBar: AppNavbarConfig = <AppNavbarConfig> {
    enabled: false,
    enabledButtons: ['home', 'reload', 'back', 'forward'],
    horizontalPosition: 'center',
    verticalPosition: 'bottom',
    width: 100
  }; // Navbar settings
  virtualKeyboard: AppVirtualKeyboardConfig = <AppVirtualKeyboardConfig>{
    enabled: false
  }; // virtual keyboard settings
  screenSaver: AppScreenSaverConfig = <AppScreenSaverConfig>{
    enabled: false,
    idleTime: 3600,
    text: 'Touch me'
  };
}
