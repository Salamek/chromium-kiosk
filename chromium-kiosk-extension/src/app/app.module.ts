import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppComponent } from './app.component';
import { NavbarComponent } from './components/navbar/navbar.component';
import { ScreensaverComponent } from './components/screensaver/screensaver.component';
import { MatButtonModule, MatDialogModule, MatIconModule, MatInputModule } from '@angular/material';
import { FlexLayoutModule } from '@angular/flex-layout';
import { FormsModule } from '@angular/forms';
import { VirtualKeyboardComponent } from './components/virtual-keyboard/virtual-keyboard.component';
import { VirtualKeyboardKeyComponent } from './components/virtual-keyboard/virtual-keyboard-key.component';
import { VirtualKeyboardService } from './components/virtual-keyboard/virtual-keyboard.service';
import { VirtualKeyboardGlobalComponent } from './components/virtual-keyboard/virtual-keyboard-global.component';
import { NgVirtualKeyboardDirective } from './components/virtual-keyboard/virtual-keyboard.directive';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

@NgModule({
  declarations: [
    AppComponent,
    NavbarComponent,
    ScreensaverComponent,
    VirtualKeyboardComponent,
    VirtualKeyboardKeyComponent,
    VirtualKeyboardGlobalComponent,
    NgVirtualKeyboardDirective
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    FlexLayoutModule,
    MatButtonModule,
    MatDialogModule,
    MatIconModule,
    FormsModule,
    MatInputModule
  ],
  providers: [
    VirtualKeyboardService
  ],
  entryComponents: [
    VirtualKeyboardComponent,
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
