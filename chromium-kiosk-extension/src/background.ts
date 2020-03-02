import { Tools } from '@app/core/tools';
import { AppConfig } from '@app/core/models/app-config';
import { DefaultSettings } from '@app/core/settings';

class TabInfo {
  completeUrl: string;
  priorCompleteUrl: string;

  construct(completeUrl: string, priorCompleteUrl: string) {
    this.completeUrl = (typeof completeUrl !== 'string') ? '' : completeUrl;
    this.priorCompleteUrl = (typeof priorCompleteUrl !== 'string') ? '' : priorCompleteUrl;
  }
}

class Background {
  idleTime: number = 0;
  homePage: string;
  whiteList: string[] = [];
  iframeEnabled: string[]|boolean;
  whiteListEnabled: boolean;
  screenSaverIdleTime: number = 0;
  screenSaverEnabled: boolean = false;
  timeOutUsingScreenSaverTime: boolean = false;
  tabsInfo = {};

  constructor(config: AppConfig) {
    this.updateConfig(config);
    this.registerListeners();
  }

  updateConfig(config: AppConfig) {
    this.idleTime = config.idleTime;
    this.homePage = config.homePage;
    this.whiteList = config.whiteList.urls || [];
    this.whiteListEnabled = config.whiteList.enabled;
    this.iframeEnabled = config.whiteList.iframeEnabled || false;
    this.screenSaverIdleTime = config.screenSaver.idleTime;
    this.screenSaverEnabled = config.screenSaver.enabled;

    // Make sure that homepage is whitelisted
    if (this.whiteListEnabled) {
      this.whiteList.push(this.homePage);
    }

    if (Array.isArray(this.iframeEnabled)) {
      // When iframe enabled is array, append about:blank, cos all iframe use it... and user will not fill it
      this.iframeEnabled.push('about:blank');
    }

    // setup
    if (this.idleTime) {
      this.timeOutUsingScreenSaverTime = false;
      chrome.idle.setDetectionInterval(this.idleTime);
    } else if (this.screenSaverIdleTime) {
      this.timeOutUsingScreenSaverTime = true;
      chrome.idle.setDetectionInterval(this.screenSaverIdleTime);
    }
    this.checkTabsForBlockedUrls();
  }

  checkTabsForBlockedUrls() {
    chrome.tabs.query({}, tabs => {
      tabs.forEach(tab => {
        this.createTabRecordIfNeeded(tab.id);
        this.tabsInfo[tab.id].completeUrl = tab.url;
        this.blockUrlIfMatch({
          tabId: tab.id,
          frameId: 0,
          url: tab.url
        });
      });
    });
  }

  completedLoadingUrlInTab(details: { tabId: string | number; frameId: number; url: any; }) {
    // We have completed loading a URL.
    this.createTabRecordIfNeeded(details.tabId);
    if (details.frameId !== 0) {
      // Only record information for the main frame
      return;
    }
    // Remember the newUrl so we can check against it the next time
    //  an event is fired.
    this.tabsInfo[details.tabId].priorCompleteUrl = this.tabsInfo[details.tabId].completeUrl;
    this.tabsInfo[details.tabId].completeUrl = details.url;
  }

  createTabRecordIfNeeded(tabId: string | number | symbol) {
    if (!this.tabsInfo.hasOwnProperty(tabId) || typeof this.tabsInfo[tabId] !== 'object') {
      // This is the first time we have encountered this tab.
      // Create an object to hold the collected info for the tab.
      this.tabsInfo[tabId] = new TabInfo();
    }
  }

  notifyOfBlockedUrl(url: string) {
    chrome.notifications.create({
      type: 'basic',
      iconUrl: Tools.getPluginAsset('assets/icon.png'),
      title: 'Blocked URL',
      message: url
    });
  }

  isUrlInWhiteList(url: string, whiteList: string[]): boolean {
    let matchesWhiteList: boolean = false;

    whiteList.forEach((whiteListItem: string) => {
      const regeEx = Tools.globToRegex(whiteListItem);
      matchesWhiteList = regeEx.test(url) || matchesWhiteList;
    });

    return matchesWhiteList;
  }

  blockUrlIfMatch(details: { tabId: any; frameId: any; url: any; }) {
    this.createTabRecordIfNeeded(details.tabId);

    if (!this.whiteList.length || !this.whiteListEnabled || details.url === 'about:blank') { // Is ignoring about blank a good idea ?
      // Return when whitelist is empty
      return;
    }
    if (!this.isUrlInWhiteList(details.url, this.whiteList)) {
      // Block this URL by navigating to the already current URL
      if (details.frameId !== 0 && this.iframeEnabled !== true) {
        // Blockation of iframe should not affect a page, so we will stop here
        // Check url if it is allowed iframe
        if (this.iframeEnabled === false || (Array.isArray(this.iframeEnabled) && !this.isUrlInWhiteList(details.url, this.iframeEnabled))) {
          // Iframes are disababled or url do not match, lets change url of iframe to blocked.html and notify about blocation
          chrome.tabs.sendMessage(details.tabId, {type: 'BlockFrame', data: details});
          // We will not notify on blocked iframes... this.notifyOfBlockedUrl(details.url);
          console.log('Blocking iframe url: ' + details.url);
        }
      } else if (details.frameId === 0) {
        // Blocation code for tabs
        let urlToUse = this.tabsInfo[details.tabId].completeUrl;
        urlToUse = (typeof urlToUse === 'string') ? urlToUse : '';

        // If tah has no urlToUse that means it is a new tab, close that tab!
        if (!urlToUse) {
          chrome.tabs.remove(details.tabId);
        } else {
          if (!this.isUrlInWhiteList(urlToUse, this.whiteList)) {
            // Url not whitelisted, go to homePage
            urlToUse = this.homePage;
          }

          chrome.tabs.update(details.tabId, { url: urlToUse }, () => {
            if (chrome.runtime.lastError) {
              if (chrome.runtime.lastError.message.indexOf('No tab with id:') > -1) {
                // Chrome is probably loading a page in a tab which it is expecting to
                //  swap out with a current tab.  Need to decide how to handle this
                //  case.
                // For now just output the error message
                console.log('Error:', chrome.runtime.lastError.message);
              } else {
                console.log('Error:', chrome.runtime.lastError.message);
              }
            }
          });
        }
        // Notify the user URL was blocked.
        this.notifyOfBlockedUrl(details.url);
      }
    }
  }

  registerListeners() {
    // Register idle listener
    chrome.idle.onStateChanged.addListener((newState) => {
      if (newState === 'idle') {
        if (this.homePage && this.idleTime > 0) {
          chrome.tabs.create({
            url: this.homePage,
            active: true
          }, (newtab) => {
            chrome.tabs.query({}, (results) => {
              for (let i = 0; i < results.length; i++) {
                const tab = results[i];
                if (tab.id !== newtab.id) {
                  chrome.tabs.remove(tab.id);
                }
              }
            });
          });
        }

        // Screensaver timeout
        if (this.screenSaverEnabled) {
          if (this.timeOutUsingScreenSaverTime) {
            chrome.tabs.query({}, tabs => {
              tabs.forEach(tab => {
                chrome.tabs.sendMessage(tab.id, {type: 'ScreenSaver', data: {show: true}});
              });
            });
          } else {
            setTimeout(() => {
              chrome.tabs.query({}, tabs => {
                tabs.forEach(tab => {
                  chrome.tabs.sendMessage(tab.id, {type: 'ScreenSaver', data: {show: true}});
                });
              });
            }, (this.screenSaverIdleTime - this.idleTime) * 1000);
          }
        }

      } else if (newState === 'active') {
        chrome.tabs.query({}, tabs => {
          tabs.forEach(tab => {
            chrome.tabs.sendMessage(tab.id, {type: 'ScreenSaver', data: {show: false}});
          });
        });
      }
    });

    // Register whitelist listeners
    chrome.webNavigation.onCompleted.addListener((details: { tabId: string | number; frameId: number; url: any; }) => this.completedLoadingUrlInTab(details));
    chrome.webNavigation.onBeforeNavigate.addListener((details: { tabId: any; frameId: any; url: any; }) => this.blockUrlIfMatch(details));
  }
}

chrome.storage.local.get(['chromium_kiosk_settings'], (config) => {

  const configFinal = (Object.keys(config).length !== 0 && config.chromium_kiosk_settings !== undefined ? <AppConfig>config.chromium_kiosk_settings : new DefaultSettings());

  // Start with initial settings if any
  const background = new Background(configFinal);

  // Watch for new settings using WS
  const webSocket = new WebSocket('ws://127.0.0.1:5678/');

  // This may not be needed, just let server trigger it on connect?
  webSocket.onopen = () => {
    webSocket.send(JSON.stringify({
      event: 'getClientConfig',
      data: {}
    }));
  };

  webSocket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.event === 'onGetClientConfig') {
      background.updateConfig(data.data);
      chrome.tabs.query({}, tabs => {
        tabs.forEach(tab => {
          chrome.tabs.sendMessage(tab.id, {type: 'AppConfig', data: data.data});
        });
      });

      chrome.storage.local.set({'chromium_kiosk_settings': data.data});
      chrome.notifications.create({
        type: 'basic',
        iconUrl: Tools.getPluginAsset('assets/icon.png'),
        title: 'Configuration updated',
        message: 'Configuration has been updated'
      });
    }
  };
});
