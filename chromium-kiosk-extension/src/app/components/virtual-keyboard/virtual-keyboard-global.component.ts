import { MatDialog, MatDialogRef } from '@angular/material';
import { VirtualKeyboardComponent } from './virtual-keyboard.component';
import { AppConfig } from '@app/core/models/app-config';
import { Component, ElementRef, OnDestroy, OnInit, HostListener } from '@angular/core';
import { AppConfigModule } from '@app/app-config.module';

import {
  alphanumericKeyboard,
  alphanumericNordicKeyboard,
  extendedKeyboard,
  extendedNordicKeyboard,
  KeyboardLayout,
  numericKeyboard,
  phoneKeyboard
} from './layouts';


@Component({
  selector: 'chromium-kioks-virtual-keyboard',
  template: ''
})
export class VirtualKeyboardGlobalComponent {
  private enabled: boolean = false;
  private opened: boolean = false;
  private focus: boolean = true;

    @HostListener('window:blur')
    onWindowBlur() {
      this.focus = false;
    }

    @HostListener('window:focus', ['$event'])
    onWindowFocus(event: Event) {
      this.proccessRawEvent(event);
      setTimeout(() => {
        this.focus = true;
      }, 0);
    }

    @HostListener('window:click', ['$event'])
    onWindowClick(event: MouseEvent) {
      this.proccessRawEvent(event);
    }

  /**
   * Constructor of the class.
   */
  public constructor(
    private dialog: MatDialog,
    private appConfigModule: AppConfigModule
  ) {
    this.appConfigModule.config.subscribe((appConfig: AppConfig) => {
      this.enabled = appConfig.virtualKeyboard.enabled;
    });
  }

  proccessRawEvent(event: any): void {
    if (!this.enabled) {
      return;
    }
    const elementRef = new ElementRef(event.target);
    const enabledInputTypes = [
      'email',
      'number',
      'password',
      'search',
      'tel',
      'text',
      'url'
    ];

    if (
      !(event.target instanceof Window) &&
      event.target.matches('input:not(.chromium-kiosk-virtual-keyboard-input), textarea') &&
      enabledInputTypes.includes(this.getType(elementRef))
    ) {
      this.openKeyboard(elementRef);
    }
  }

  /**
   * Method to open virtual keyboard
   */
  private openKeyboard(inputElement: ElementRef) {
    if (!this.opened && this.focus) {
      this.opened = true;

      let dialogRef: MatDialogRef<VirtualKeyboardComponent>;

      dialogRef = this.dialog.open(VirtualKeyboardComponent);
      dialogRef.componentInstance.inputElement = inputElement;
      dialogRef.componentInstance.layout = this.getLayout(inputElement);
      dialogRef.componentInstance.placeholder = inputElement.nativeElement.placeholder || '';
      dialogRef.componentInstance.type = this.getType(inputElement);

      dialogRef
        .afterClosed()
        .subscribe(() => {
          setTimeout(() => {
            this.opened = false;
          }, 0);
        });
    }
  }

  private getLayout(inputElement: ElementRef): KeyboardLayout {
    let layout;

    switch (this.getType(inputElement)) {
      case 'number':
        layout = numericKeyboard;
        break;
      case 'tel':
        layout = phoneKeyboard;
        break;
      default:
        layout = extendedKeyboard;
        break;
    }

    return layout;
  }

  private getType(inputElement: ElementRef): string {
    return inputElement.nativeElement.type;
  }
}
