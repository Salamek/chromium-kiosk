import { AppConfig } from '@app/core/models/app-config';
import { Observable, BehaviorSubject } from 'rxjs';

export class AppConfigModule {
  configSubject: BehaviorSubject<AppConfig>;
  constructor(
    config: AppConfig
  ) {
    this.configSubject = new BehaviorSubject<AppConfig>(config);

    // Register chrome message handler
    if (chrome.runtime !== undefined) {
      chrome.runtime.onMessage.addListener((msg, _, sendResponse) => {
        if (msg.type === 'AppConfig') {
          this.configSubject.next(msg.data);
          sendResponse(true);
        }
      });
    }
  }

  get config(): Observable<AppConfig> {
    return this.configSubject.asObservable();
  }

}
