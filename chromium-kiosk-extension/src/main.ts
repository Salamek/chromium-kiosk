import { enableProdMode } from '@angular/core';
import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';

import { AppConfigModule } from './app/app-config.module';
import { AppModule } from './app/app.module';
import { Tools } from '@app/core/tools';
import { AppConfig } from '@app/core/models/app-config';
import { DefaultSettings } from '@app/core/settings';
import { environment } from './environments/environment';

if (environment.production) {
  enableProdMode();
}

// Create app-root in body before app stars


function loadApp(config: AppConfig) {
  const appConfigModule = new AppConfigModule(config);
  platformBrowserDynamic([{ provide: AppConfigModule, useValue: appConfigModule}])
    .bootstrapModule(AppModule)
    .catch((err: any) => console.error(err));
}


const blockedFrames: string[] = [];
document.onreadystatechange = () => {
  checkBlockedIframes(blockedFrames);
  if (document.readyState === 'complete') {
    const bodyies = document.getElementsByTagName('body');

    if (bodyies.length > 0) {
      const body = bodyies[0];

      const appRoot = document.createElement('chromium-kiosk-root');

      body.insertBefore(appRoot, body.children[0]);

      if (chrome.storage !== undefined) {

        chrome.storage.local.get(['chromium_kiosk_settings'], (config) => {
          const configFinal = (Object.keys(config).length !== 0 && config.chromium_kiosk_settings !== undefined ? <AppConfig>config.chromium_kiosk_settings : new DefaultSettings());
          loadApp(configFinal);
        });
      } else {
        loadApp(new DefaultSettings());
      }
    }
  }
};


function checkBlockedIframes(urlList: string[]) {
  const iframes = document.getElementsByTagName('iframe');
  for (let i = 0; i < iframes.length; ++i) {
      if (urlList.includes(iframes[i].src)) {
        iframes[i].src = Tools.getPluginAsset('blocked_frame.html');
      }
  }
}

// Frame blocation code
if (chrome.runtime !== undefined) {
  chrome.runtime.onMessage.addListener((msg, _, sendResponse) => {
    if (msg.type === 'BlockFrame') {
      // Add frame into list
      blockedFrames.push(msg.data.url);
      checkBlockedIframes(blockedFrames);
      sendResponse(true);
    }
  });
}
