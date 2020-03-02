import { Component, OnInit, OnDestroy, ChangeDetectorRef } from '@angular/core';
import { AppConfig } from '@app/core/models/app-config';
import { Tools } from '@app/core/tools';
import { AppConfigModule } from '@app/app-config.module';
import { Subscription, Observable } from 'rxjs';

@Component({
  selector: 'chromium-kiosk-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss']
})
export class NavbarComponent implements OnInit, OnDestroy {
  enabled: boolean = false;
  barClasses: string[] = ['center', 'bottom', 'center-full-width']; // ['left|center|right', 'bottom|top']
  homePage: string;
  width: number = 100;
  marginLeft: number = 0;
  marginRight: number = 0;
  buttons: {};
  buttonsEnabled: {}[];

  _configSub: Subscription;

  constructor(
    private appConfigModule: AppConfigModule,
    private ref: ChangeDetectorRef) {
  }

  ngOnInit(): void {
    this.buttons = {
      home: {
        icon: Tools.getPluginAsset('assets/bar-controls/home.png'),
        title: 'Home',
        callback: () => window.location.href = this.homePage
      },
      reload: {
        icon: Tools.getPluginAsset('assets/bar-controls/reload.png'),
        title: 'Reload',
        callback: () => window.location.reload()
      },
      back: {
        icon: Tools.getPluginAsset('assets/bar-controls/back.png'),
        title: 'Back',
        callback: () => window.history.back()
      },
      forward: {
        icon: Tools.getPluginAsset('assets/bar-controls/forward.png'),
        title: 'Forward',
        callback: () => window.history.forward()
      },
    };

    this._configSub = this.appConfigModule.config.subscribe((appConfig: AppConfig) => {
      this.enabled = appConfig.navBar.enabled;
      this.homePage = appConfig.homePage;
      this.width = appConfig.navBar.width;

      if (appConfig.navBar.horizontalPosition === 'left') {
        this.marginLeft = 0;
        this.marginRight = (100 - appConfig.navBar.width);
      } else if (appConfig.navBar.horizontalPosition === 'right') {
        this.marginRight = 0;
        this.marginLeft = (100 - appConfig.navBar.width);
      } else { // Center -> default
        this.marginLeft = this.marginRight = (100 - appConfig.navBar.width) / 2;
      }

      const buttonsEnabled: {}[] = [];
      const toEnable = appConfig.navBar.enabledButtons || Object.keys(this.buttons);
      toEnable.forEach((buttonKey: string) => {
        if (buttonKey in this.buttons) {
          buttonsEnabled.push(this.buttons[buttonKey]);
        }
      });
      this.buttonsEnabled = buttonsEnabled;

      const barClasses: string[] = [appConfig.navBar.horizontalPosition || 'center', appConfig.navBar.verticalPosition || 'bottom'];

      if (appConfig.navBar.width === 100) {
        barClasses.push('center-full-width');
      }

      this.barClasses = barClasses;
      this.ref.detectChanges();
    });

  }

  onButtonClick(button: any) {
    button.callback();
  }

  ngOnDestroy () {
    this._configSub.unsubscribe();
  }
}
