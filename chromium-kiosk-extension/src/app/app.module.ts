import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppComponent } from './app.component';
import { NavbarComponent } from './components/navbar/navbar.component';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogModule } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
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
