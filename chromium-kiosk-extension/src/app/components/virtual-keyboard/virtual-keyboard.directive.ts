import { Directive, ElementRef, HostListener, Input } from '@angular/core';
import { MatDialog, MatDialogRef } from '@angular/material';

import { VirtualKeyboardComponent } from './virtual-keyboard.component';
import {
  alphanumericKeyboard,
  alphanumericNordicKeyboard,
  extendedKeyboard,
  extendedNordicKeyboard,
  KeyboardLayout,
  numericKeyboard,
  phoneKeyboard
} from './layouts';

@Directive({
  selector: 'input:not(.chromium-kiosk-virtual-keyboard-input), textarea'
})

export class NgVirtualKeyboardDirective {
  private opened = false;
  private focus = true;

  @HostListener('window:blur')
  onWindowBlur() {
    this.focus = false;
  }

  @HostListener('window:focus')
  onWindowFocus() {
    setTimeout(() => {
      this.focus = true;
    }, 0);
  }

  @HostListener('focus')
  onFocus() {
    this.openKeyboard();
  }

  @HostListener('click')
  onClick() {
    this.openKeyboard();
  }

  /**
   * Constructor of the class.
   */
  public constructor(
    private element: ElementRef,
    private dialog: MatDialog,
  ) { }

  /**
   * Method to open virtual keyboard
   */
  private openKeyboard() {
    if (!this.opened && this.focus) {
      this.opened = true;

      let dialogRef: MatDialogRef<VirtualKeyboardComponent>;

      dialogRef = this.dialog.open(VirtualKeyboardComponent);
      dialogRef.componentInstance.inputElement = this.element;
      dialogRef.componentInstance.layout = this.getLayout();
      dialogRef.componentInstance.placeholder = this.getPlaceHolder();
      dialogRef.componentInstance.type = this.getType();

      dialogRef
        .afterClosed()
        .subscribe(() => {
          setTimeout(() => {
            this.opened = false;
          }, 0);
        });
    }
  }

  /**
   * Getter for used keyboard layout.
   */
  private getLayout(): KeyboardLayout {
    let layout;

    switch (this.getType()) {
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

  /**
   * Getter for used placeholder for virtual keyboard input field.
   */
  private getPlaceHolder(): string {
    return this.element.nativeElement.placeholder;
  }

  /**
   * Getter for used type for virtual keyboard input field.
   */
  private getType(): string {
    return this.element.nativeElement.type;
  }
}
