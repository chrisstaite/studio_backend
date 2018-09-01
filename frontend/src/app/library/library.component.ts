import { Component, Inject, OnInit, Pipe, PipeTransform } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { MatDialog, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material';
import { DirectoryPickerService } from '../directory-picker.service';
import { Subject, Observable, Subscription } from 'rxjs';
import { debounceTime } from 'rxjs/operators';
import { DragulaService } from 'ng2-dragula';

enum SongState {
  Stopped,
  Loading,
  Playing
};

class Song {

  _SongState = SongState;

  state: SongState = SongState.Stopped;

  constructor(public id: number,
              public title: string,
              public artist: string,
              public location: string,
              public length: number) { }

  play(element) {
    this.state = SongState.Loading;
    element.src = '/library/track/' + this.id;
    element.load();
    let promise = element.play();
    if (promise !== undefined) {
      promise.then(_ => {
        this.state = SongState.Playing;
      }).catch(error => {
        this.state = SongState.Stopped;
      });
    }
  }

  stop(element) {
    this.state = SongState.Stopped;
    element.src = '';
  }
}

class Playlist {

  private _tracks: Array<Song>;
  private _tracksSubject: Subject<Array<Song>> = new Subject<Array<Song>>();

  constructor(public id: number, public name: string, private http: HttpClient) { }

  load() {
    this.http.get<any>('/playlist/' + this.id).subscribe((data: any) => {
      this._tracks = data.map(function (track) {
        return new Song(track.id, track.title, track.artist, track.location, track.length);
      });
      this._tracksSubject.next(this._tracks);
    });
  }

  get tracks(): Observable<Array<Song>> {
    return this._tracksSubject.asObservable();
  }

  add(tracks: Array<Song>) {
    this._tracks.push(...tracks);
    this._tracksSubject.next(this._tracks);
    this._update();
  }

  moveTrack(index: number, after: number) {
    if ((after === null && index == this._tracks.length) || (after !== null && index == after - 1)) {
      // Already in the right place, nothing to do
      return;
    }
    var track = this._tracks.splice(index, 1)[0];
    if (after === null) {
      this._tracks.push(track);
    } else {
      this._tracks.splice(after, 0, track);
    }
    this._tracksSubject.next(this._tracks);
    this._update();
  }

  remove(tracks: Array<Song>) {
    tracks.forEach(track => {
      let index = this._tracks.indexOf(track);
      if (index > -1) {
        this._tracks.splice(index, 1);
      }
    });
    this._tracksSubject.next(this._tracks);
    this._update();
  }

  private _update() {
    let ids = this._tracks.map(track => track.id);
    this.http.put('/playlist/' + this.id, {'tracks': ids}).subscribe();
  }

}

@Pipe({
  name: 'songTime'
})
export class SongTimePipe implements PipeTransform {
    transform(value: number): string {
       const minutes: number = Math.floor(value / 60);
       const seconds: number = Math.round(value % 60);
       return minutes + ':' + (seconds < 10 ? '0' : '') + seconds;
    }
}

@Component({
  selector: 'app-library',
  templateUrl: './library.component.html',
  styleUrls: ['./library.component.css']
})
export class LibraryComponent implements OnInit {

  private _query: string = "";
  private _songs: Subject<Array<Song>> = new Subject<Array<Song>>();
  private _songCount: number = 0;
  private _updateDebounce: Subject<void> = new Subject<void>();
  private _pageSize: number = 10;
  private _page: number = 0;
  private _currentSong: Song = null;
  private _playbackElement: any = new Audio();
  displayColumns: Array<string> = ['play', 'artist', 'title', 'length'];
  playlistDisplayColumns: Array<string> = ['artist', 'title', 'length'];
  playlists: Array<Playlist> = [];
  selected: Array<Song> = [];
  playlistSelected: Array<Song> = [];
  currentEdit: Song;
  private _playlist: Playlist;
  private _subs = new Subscription();

  constructor(private dialog: MatDialog, private http: HttpClient, private dragulaService: DragulaService) {
    this._subs.add(this._updateDebounce.pipe(debounceTime(200)).subscribe(() => this._updateList()));
  }

  ngOnInit() {
    this.dragulaService.createGroup('playlist-tracks', {
      revertOnSpill: true,
      accepts: function (el, target, source, sibling) {
        return sibling === null || !sibling.classList.contains('mat-header-row');
      },
      moves: function (el:any, container:any, handle:any):any {
        return !el.classList.contains('mat-header-row');
      }
    });

    this._subs.add(
      this.dragulaService.drop('playlist-tracks').subscribe(
        ({ name, el, target, source, sibling }) => {
          var index = Number(el.getAttribute('data-index'));
          var insertBefore = sibling === null ? null : Number(sibling.getAttribute('data-index'));
          this._playlist.moveTrack(index, insertBefore);
        }
      )
    );

    this._updateList();

    this.http.get<any>('/playlist').subscribe((data: any) => {
      let http = this.http;
      this.playlists = data.map(function (playlist) {
        return new Playlist(playlist.id, playlist.name, http);
      });
    });
  }

  ngOnDestroy() {
    this._subs.unsubscribe();
  }

  saveSong() {
    if (this.currentEdit) {
      this.http.put(
        '/library/track/' + this.currentEdit.id,
        {'artist': this.currentEdit.artist, 'title': this.currentEdit.title}
      ).subscribe();
    }
  }

  toggle(song: Song) {
    let index = this.selected.indexOf(song);
    if (index > -1) {
      this.selected.splice(index, 1);
    } else {
      this.selected.push(song);
    }
  }

  playlistToggle(song: Song) {
    let index = this.playlistSelected.indexOf(song);
    if (index > -1) {
      this.playlistSelected.splice(index, 1);
    } else {
      this.playlistSelected.push(song);
    }
  }

  set playlist(playlist: Playlist) {
    this._playlist = playlist;
    if (this._playlist) {
      this._playlist.load();
    }
  }

  get playlist(): Playlist {
    return this._playlist;
  }

  set currentSong(song: Song) {
    if (song == this._currentSong) {
      this._currentSong.stop(this._playbackElement);
      this._currentSong = null;
    } else {
      if (this._currentSong != null) {
        this._currentSong.stop(this._playbackElement);
      }
      this._currentSong = song;
      this._currentSong.play(this._playbackElement);
    }
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

  get songs(): Observable<Array<Song>> {
    return this._songs.asObservable();
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
      let songs = data.tracks.map(function (track) {
        return new Song(track.id, track.title, track.artist, track.location, track.length);
      });
      this.selected = [];
      this._songCount = data.count;
      this._songs.next(songs);
    });
  }

  libraryRoots() {
    this.dialog.open(LibraryRootsDialog);
  }

  newPlaylist() {
    this.dialog.open(NewPlaylistDialog, { data: { parent: this } });
  }

}

@Component({
  templateUrl: './roots-dialog.html',
  styleUrls: ['./roots-dialog.css']
})
export class LibraryRootsDialog implements OnInit {

  roots: Array<string> = [];
  private _subs = new Subscription();

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
    this._subs.add(this.picker.pick().subscribe((directory: string) => {
      this.http.post('/library', { 'directory': directory }).subscribe(() => {
        roots.push(directory);
      });
    }));
  }

  ngOnDestroy() {
    this._subs.unsubscribe();
  }

}

@Component({
  templateUrl: './playlist-dialog.html',
  styleUrls: ['./playlist-dialog.css']
})
export class NewPlaylistDialog implements OnInit {

  constructor(
    private http: HttpClient,
    private dialog: MatDialogRef<NewPlaylistDialog>,
    @Inject(MAT_DIALOG_DATA) private data: any
   ) { }

  ngOnInit() {
  }

  onNoClick(): void {
    this.dialog.close();
  }

  newPlaylist(name: string) {
    this.http.post<number>('/playlist', {'name': name}).subscribe(id => {
      this.data.parent.playlists.push(new Playlist(id, name, this.http));
      this.dialog.close();
    });
  }

}
