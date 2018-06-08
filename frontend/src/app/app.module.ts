import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import {
  MatCardModule,
  MatButtonModule,
  MatIconModule
} from '@angular/material';

import { AppComponent } from './app.component';
import { InputListComponent } from './input-list/input-list.component';
import { OutputListComponent } from './output-list/output-list.component';
import { MixerListComponent } from './mixer-list/mixer-list.component';

@NgModule({
  declarations: [
    AppComponent,
    InputListComponent,
    OutputListComponent,
    MixerListComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
