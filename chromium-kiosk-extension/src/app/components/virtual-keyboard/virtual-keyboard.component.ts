import { Component, ElementRef, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';


import { keyboardCapsLockLayout, KeyboardLayout } from './layouts';
import { VirtualKeyboardService } from './virtual-keyboard.service';
import { KeyPressInterface } from './key-press.interface';

@Component({
  selector: 'virtual-keyboard',
  templateUrl: './virtual-keyboard.component.html',
  styleUrls: ['virtual-keyboard.component.scss']
})

export class VirtualKeyboardComponent implements OnInit, OnDestroy {
  @ViewChild('keyboardInput', {static: true}) keyboardInput!: ElementRef;

  public inputElement!: ElementRef;
  public layout!: KeyboardLayout;
  public placeholder!: string;
  public type!: string;
  public disabled!: boolean;
  public maxLength!: number|string;

  private caretPosition!: number;
  private shift = false;

  /**
   * Helper method to set cursor in input to correct place.
   *
   */
  private static setSelectionRange(
    input: any,
    start: number,
    end: number
  ): void {
    if (input.setSelectionRange) {
      input.focus();
      const originalType = input.type;
      input.type = 'text';
      input.setSelectionRange(start, end);
      input.type = originalType;

    } else if (input.createTextRange) {
      const range = input.createTextRange();

      range.collapse(true);
      range.moveEnd('character', end);
      range.moveStart('character', start);
      range.select();
    }
  }

  /**
   * Constructor of the class.
   *
   */
  public constructor(
    public dialogRef: MatDialogRef<VirtualKeyboardComponent>,
    private virtualKeyboardService: VirtualKeyboardService
  ) { }

  /**
   * On init life cycle hook, this will do following:
   *  1) Set focus to virtual keyboard input field
   *  2) Subscribe to following
   *    2.1) Shift key, this is needed in keyboard event dispatches
   *    2.2) CapsLock key, this will change keyboard layout
   *    2.3) Caret position in virtual keyboard input
   *  3) Reset of possible previously tracked caret position
   */
  public ngOnInit(): void {
    setTimeout(() => {
      this.keyboardInput.nativeElement.focus();
    }, 0);

    this.virtualKeyboardService.shift$.subscribe((shift: boolean) => {
      this.shift = shift;
    });

    this.virtualKeyboardService.capsLock$.subscribe((capsLock: boolean) => {
      this.layout = keyboardCapsLockLayout(this.layout, capsLock);
    });

    this.virtualKeyboardService.caretPosition$.subscribe((caretPosition: number) => {
      this.caretPosition = caretPosition;

      setTimeout(() => {
        VirtualKeyboardComponent.setSelectionRange(this.keyboardInput.nativeElement, caretPosition, caretPosition);
      }, 0);
    });

    if (this.inputElement.nativeElement.value.length) {
      this.virtualKeyboardService.setCaretPosition(this.inputElement.nativeElement.value.length);
    }

    this.maxLength = this.inputElement.nativeElement.maxLength > 0 ? this.inputElement.nativeElement.maxLength : '';

    this.checkDisabled();
  }

  /**
   * On destroy life cycle hook, in this we want to reset virtual keyboard service states on following:
   *  - Shift
   *  - CapsLock
   */
  public ngOnDestroy(): void {
    this.virtualKeyboardService.reset();
  }

  /**
   * Method to close virtual keyboard dialog
   */
  public close(): void {
    this.dialogRef.close();
  }

  /**
   * Method to update caret position. This is called on click event in virtual keyboard input element.
   */
  public updateCaretPosition(): void {
    this.virtualKeyboardService.setCaretPosition(this.keyboardInput.nativeElement.selectionStart);
  }

  /**
   * Method to handle actual "key" press from virtual keyboard.
   *  1) Key is "Special", process special key event
   *  2) Key is "Normal"
   *    - Append this key value to input
   *    - Dispatch DOM events to input element
   *    - Toggle Shift key if it's pressed
   *
   */
  public keyPress(event: KeyPressInterface): void {
    if (event.special) {
      this.handleSpecialKey(event);
    } else {
      this.handleNormalKey(event.keyValue);

      this.dispatchEvents(event);

      // Toggle shift if it's activated
      if (this.shift) {
        this.virtualKeyboardService.toggleShift();
      }
    }

    this.checkDisabled();
  }

  /**
   * Method to check is virtual keyboard input is disabled.
   */
  private checkDisabled(): void {
    const maxLength = this.inputElement.nativeElement.maxLength;
    const valueLength = this.inputElement.nativeElement.value.length;

    this.disabled = maxLength > 0 && valueLength >= maxLength;
  }

  /**
   * Method to handle "normal" key press event, this will add specified character to input value.
   *
   */
  private handleNormalKey(keyValue: string): void {
    let value = '';

    // We have caret position, so attach character to specified position
    if (!isNaN(this.caretPosition)) {
      value = [
        this.inputElement.nativeElement.value.slice(0, this.caretPosition),
        keyValue,
        this.inputElement.nativeElement.value.slice(this.caretPosition)
      ].join('');

      // Update caret position
      this.virtualKeyboardService.setCaretPosition(this.caretPosition + 1);
    } else {
      value = `${this.inputElement.nativeElement.value}${keyValue}`;
    }

    // And finally set new value to input
    this.inputElement.nativeElement.value = value;
  }

  /**
   * Method to handle "Special" key press events.
   *  1) Enter
   *  2) Escape, close virtual keyboard
   *  3) Backspace, remove last character from input value
   *  4) CapsLock, toggle current layout state
   *  6) Shift, toggle current layout state
   *  5) SpaceBar
   */
  private handleSpecialKey(event: KeyPressInterface): void {
    switch (event.keyValue) {
      case 'Enter':
        this.close();
        break;
      case 'Escape':
        this.close();
        break;
      case 'Backspace':
        const currentValue = this.inputElement.nativeElement.value;

        // We have a caret position, so we need to remove char from that position
        if (!isNaN(this.caretPosition)) {
          // And current position must > 0
          if (this.caretPosition > 0) {
            const start = currentValue.slice(0, this.caretPosition - 1);
            const end = currentValue.slice(this.caretPosition);

            this.inputElement.nativeElement.value = `${start}${end}`;

            // Update caret position
            this.virtualKeyboardService.setCaretPosition(this.caretPosition - 1);
          }
        } else {
          this.inputElement.nativeElement.value = currentValue.substring(0, currentValue.length - 1);
        }

        // Set focus to keyboard input
        this.keyboardInput.nativeElement.focus();
        break;
      case 'CapsLock':
        this.virtualKeyboardService.toggleCapsLock();
        break;
      case 'Shift':
        this.virtualKeyboardService.toggleShift();
        break;
      case 'SpaceBar':
        this.handleNormalKey(' ');
        break;
    }
  }

  /**
   * Method to dispatch necessary keyboard events to current input element.
   *
   * @see https://w3c.github.io/uievents/tools/key-event-viewer.html
   *
   */
  private dispatchEvents(event: KeyPressInterface) {
    const eventInit: KeyboardEventInit = {
      bubbles: true,
      cancelable: true,
      shiftKey: this.shift,
      key: event.keyValue,
      code: `Key${event.keyValue.toUpperCase()}}`,
      location: 0
    };

    // Simulate all needed events on base element
    this.inputElement.nativeElement.dispatchEvent(new KeyboardEvent('keydown', eventInit));
    this.inputElement.nativeElement.dispatchEvent(new KeyboardEvent('keypress', eventInit));
    this.inputElement.nativeElement.dispatchEvent(new Event('input', {bubbles : true}));
    this.inputElement.nativeElement.dispatchEvent(new KeyboardEvent('keyup', eventInit));

    // And set focus to input
    this.keyboardInput.nativeElement.focus();
  }
}
