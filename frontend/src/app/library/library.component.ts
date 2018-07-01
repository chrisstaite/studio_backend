import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { MatDialog, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material';
import { DirectoryPickerService } from '../directory-picker.service';

@Component({
  selector: 'app-library',
  templateUrl: './library.component.html',
  styleUrls: ['./library.component.css']
})
export class LibraryComponent implements OnInit {

  constructor(private dialog: MatDialog) { }

  ngOnInit() {
  }

  libraryRoots() {
    this.dialog.open(LibraryRootsDialog, { data: {} });
  }

}

@Component({
  templateUrl: './roots-dialog.html',
  styleUrls: ['./roots-dialog.css']
})
export class LibraryRootsDialog implements OnInit {

  roots: Array<string> = [];

  constructor(
    private http: HttpClient,
    private picker: DirectoryPickerService,
    private dialog: MatDialogRef<LibraryRootsDialog>
   ) { }

  ngOnInit() {
    this.http.get<Array<string>>('/library').subscribe(roots => this.roots = roots);
  }

  onNoClick(): void {
    this.dialog.close();
  }

  newRoot() {
    let roots = this.roots;
    this.picker.pick().subscribe((directory: string) => {
      this.http.post('/library', { 'directory': directory }).subscribe(() => {
        roots.push(directory);
      });
    });
  }

}
