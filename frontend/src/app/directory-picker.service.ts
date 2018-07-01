import { Injectable } from '@angular/core';
import { MatDialog } from '@angular/material';
import { Observable, Observer } from 'rxjs';
import { DirectoryPickerComponent } from './directory-picker/directory-picker.component';

@Injectable({
  providedIn: 'root'
})
export class DirectoryPickerService {

  constructor(private dialog: MatDialog) { }

  private openDialog(observer: Observer<string>) {
    this.dialog.open(DirectoryPickerComponent, { data: observer });
  }

  pick() {
    return new Observable<string>(this.openDialog.bind(this));
  }

}
