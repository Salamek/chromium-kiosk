import { Component, OnInit, Input, EventEmitter, Output } from '@angular/core';

import { KeyPressInterface } from './key-press.interface';
import { isSpacer, isSpecial, notDisabledSpecialKeys, specialKeyIcons, specialKeyTexts } from './layouts';

@Component({
  selector: 'virtual-keyboard-key',
  template: `
    <button
      mat-raised-button
      color="primary"
      fxFlex="{{ flexValue }}"
      [class.spacer]="spacer"
      [disabled]="isDisabled()"
      (click)="onKeyPress()"
    >
      <span *ngIf="!special">{{ keyValue }}</span>

      <span *ngIf="special">
        <mat-icon *ngIf="icon">{{ icon }}</mat-icon>

        {{ text }}
      </span>
    </button>
  `,
  styles: [`
    .mat-button,
    .mat-icon-button,
    .mat-raised-button {
      min-width: 64px;
      min-height: 64px;
      padding: 0;
      margin: 2px;
      font-size: 32px;
      line-height: 32px;
    }

    .mat-button.spacer,
    .mat-icon-button.spacer,
    .mat-raised-button.spacer {
      background-color: transparent;
    }
  `]
})

export class VirtualKeyboardKeyComponent implements OnInit {
  @Input() key!: string;
  @Input() disabled!: boolean;
  @Output() keyPress = new EventEmitter<KeyPressInterface>();

  public special = false;
  public spacer = false;
  public flexValue!: string;
  public keyValue!: string;
  public icon!: string;
  public text!: string;

  /**
   * Constructor of the class.
   */
  public constructor() { }

  /**
   * On init life cycle hook, within this we'll initialize following properties:
   *  - special
   *  - keyValue
   *  - flexValue
   */
  public ngOnInit(): void {
    let multiplier = 1;
    let fix = 0;

    if (this.key.length > 1) {
      this.spacer = isSpacer(this.key);
      this.special = isSpecial(this.key);

      const matches = /^(\w+)(:(\d+(\.\d+)?))?$/g.exec(this.key);
      if (matches) {
        this.keyValue = matches[1];

        if (matches[3]) {
          multiplier = parseFloat(matches[3]);
          fix = (multiplier - 1) * 4;
        }
      }
    } else {
      this.keyValue = this.key;
    }

    if (this.special) {
      if (specialKeyIcons.hasOwnProperty(this.keyValue)) {
        this.icon = specialKeyIcons[this.keyValue];
      } else if (specialKeyTexts.hasOwnProperty(this.keyValue)) {
        this.text = specialKeyTexts[this.keyValue];
      }
    }

    this.flexValue = `${multiplier * 64 + fix}px`;
  }

  /**
   * Method to check if key is disabled or not.
   */
  public isDisabled(): boolean {
    if (this.spacer) {
      return true;
    } else if (this.disabled && notDisabledSpecialKeys.indexOf(this.keyValue) !== -1) {
      return false;
    } else {
      return this.disabled;
    }
  }

  /**
   * Method to handle actual "key" press from virtual keyboard.
   *  1) Key is "Special", process special key event
   *  2) Key is "Normal", append this key value to input
   */
  public onKeyPress(): void {
    this.keyPress.emit({special: this.special, keyValue: this.keyValue, key: this.key});
  }
}
