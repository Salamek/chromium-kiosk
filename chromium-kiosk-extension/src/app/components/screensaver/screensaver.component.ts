import { Component, OnInit, OnDestroy, ChangeDetectorRef, ElementRef } from '@angular/core';
import { AppConfig } from '@app/core/models/app-config';
import { AppConfigModule } from '@app/app-config.module';
import { Subscription } from 'rxjs';

@Component({
  selector: 'chromium-kiosk-screensaver',
  templateUrl: './screensaver.component.html',
  styleUrls: ['./screensaver.component.scss']
})
export class ScreensaverComponent implements OnInit, OnDestroy {
  enabled: boolean = false;
  displayed: boolean = false;
  text: string;
  letters: string[];
  _configSub: Subscription;

  constructor(
    private appConfigModule: AppConfigModule,
    private elementRef: ElementRef,
    private ref: ChangeDetectorRef) {
  }

  ngOnInit(): void {
    this._configSub = this.appConfigModule.config.subscribe((appConfig: AppConfig) => {
      this.enabled = appConfig.screenSaver.enabled;
      this.text = appConfig.screenSaver.text;
      this.letters = [];
      this.letters = appConfig.screenSaver.text.split('');

      this.ref.detectChanges();
      this.appyDelayAnimation();
    });

    // Register chrome message handler
    if (chrome.runtime !== undefined) {
      chrome.runtime.onMessage.addListener((msg, _, sendResponse) => {
        if (msg.type === 'ScreenSaver') {
          this.displayed = msg.data.show;
          this.ref.detectChanges();
          this.appyDelayAnimation();
          sendResponse(true);
        }
      });
    }
  }

  ngAfterViewInit() {
    // you'll get your through 'elements' below code
    this.appyDelayAnimation();
  }

  appyDelayAnimation() {
    const letters = this.elementRef.nativeElement.querySelectorAll('.letter');
    letters.forEach((letter: any) => {
      letter.style.animation = 'none';
      letter.style.animation = null;
      letter.className = '';
    });

    let j = 0;
    function applyBounce() {
      setTimeout(() => {
        if (letters[j]) {
            letters[j].className = 'letter bounce-me';
        }
        j++;

        if (j < letters.length) {
          applyBounce();
        }
      }, 250);
    }

    applyBounce();
  }

  ngOnDestroy() {
    this._configSub.unsubscribe();
  }
}
