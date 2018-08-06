import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { MatDialog, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material';
import { DirectoryPickerService } from '../directory-picker.service';
import { Subject } from 'rxjs';
import { debounceTime } from 'rxjs/operators';

class Song {
  constructor(public id: number, public title: string, public artist: string, public location: string) { }
}

@Component({
  selector: 'app-library',
  templateUrl: './library.component.html',
  styleUrls: ['./library.component.css']
})
export class LibraryComponent implements OnInit {

  private _query: string = "";
  private _songs: Array<Song> = [];
  private _songCount: number = 0;
  private _updateDebounce: Subject<void> = new Subject<void>();
  private _pageSize: number = 10;
  private _page: number = 0;

  constructor(private dialog: MatDialog, private http: HttpClient) {
    this._updateDebounce.pipe(debounceTime(200)).subscribe(() => this._updateList());
  }

  ngOnInit() {
    this._updateDebounce.next();
  }

  get query(): string {
    return this._query;
  }

  get songCount(): number {
    return this._songCount;
  }

  set query(query: string) {
    if (this._query != query) {
      this._query = query;
      this.page = 0;
      this._updateDebounce.next();
    }
  }

  get songs(): Array<Song> {
    return this._songs;
  }

  get page(): number {
    return this._page;
  }

  set page(page: number) {
    if (this._page != page) {
      this._page = page;
      this._updateDebounce.next();
    }
  }

  get pageSize(): number {
    return this._pageSize;
  }

  set pageSize(pageSize: number) {
    if (this._pageSize != pageSize) {
      this._pageSize = pageSize;
      this._updateDebounce.next();
    }
  }

  private _updateList() {
    let query = {'results': String(this._pageSize), 'page': String(this._page)};
    if (this.query != '') {
      query['query'] = this.query;
    }
    let httpParams = new HttpParams({ fromObject: query });
    this.http.get<any>('/library/track', {params: httpParams}).subscribe((data: any) => {
      this._songs = data.tracks.map(function (track) {
        return new Song(track.id, track.title, track.artist, track.location);
      });
      this._songCount = data.count;
    });
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
