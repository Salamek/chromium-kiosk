import { Injectable } from '@angular/core';
import { ReplaySubject} from 'rxjs/internal/ReplaySubject';

@Injectable()
export class VirtualKeyboardService {
  public shift$: ReplaySubject<boolean> = new ReplaySubject(1);
  public capsLock$: ReplaySubject<boolean> = new ReplaySubject(1);
  public caretPosition$: ReplaySubject<number> = new ReplaySubject(1);

  private capsLock = false;
  private shift = false;

  /**
   * Setter for Shift value, note that this also sets CapsLock value.
   */
  public setShift(value: boolean) {
    this.shift = value;
    this.shift$.next(this.shift);

    this.setCapsLock(this.shift);
  }

  /**
   * Setter for CapsLock value
   */
  public setCapsLock(value: boolean) {
    this.capsLock = value;
    this.capsLock$.next(value);
  }

  /**
   * Toggle for Shift, note that this also toggles CapsLock
   */
  public toggleShift(): void {
    this.shift = !this.shift;
    this.shift$.next(this.shift);

    this.setCapsLock(this.shift);
  }

  /**
   * Toggle for CapsLock
   */
  public toggleCapsLock() {
    this.capsLock = !this.capsLock;
    this.capsLock$.next(this.capsLock);
  }

  /**
   * Setter for caret position value.
   */
  public setCaretPosition(position: number) {
    this.caretPosition$.next(position);
  }

  /**
   * Method to reset Shift and CapsLock values to default ones.
   */
  public reset() {
    this.setShift(false);
  }
}
