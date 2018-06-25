import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClientModule } from '@angular/common/http';

import {
  MatCardModule,
  MatButtonModule,
  MatIconModule,
  MatTooltipModule,
  MatDialogModule,
  MatExpansionModule,
  MatInputModule,
  MatSelectModule,
  MatGridListModule,
  MatSliderModule
} from '@angular/material';

import { AppComponent } from './app.component';
import { InputListComponent, NewInputDialog } from './input-list/input-list.component';
import { OutputListComponent, NewOutputDialog } from './output-list/output-list.component';
import { MixerListComponent } from './mixer-list/mixer-list.component';
import { MixerComponent } from './mixer/mixer.component';

@NgModule({
  declarations: [
    AppComponent,
    InputListComponent,
    NewInputDialog,
    OutputListComponent,
    NewOutputDialog,
    MixerListComponent,
    MixerComponent
  ],
  entryComponents: [
    NewInputDialog,
    NewOutputDialog
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    HttpClientModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatTooltipModule,
    MatDialogModule,
    MatExpansionModule,
    MatInputModule,
    MatSelectModule,
    MatGridListModule,
    MatSliderModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
