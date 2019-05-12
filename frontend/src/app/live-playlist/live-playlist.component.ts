import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { DragulaService } from 'ng2-dragula';

class Song {

  constructor(public id: number,
              public title: string,
              public artist: string,
              public started: Date,
              public length: number) { }

  playtime() {
    return new Date().getTime() - this.started.getTime();
  }

}

@Component({
  selector: 'app-live-playlist',
  templateUrl: './live-playlist.component.html',
  styleUrls: ['./live-playlist.component.css']
})
export class LivePlaylistComponent implements OnInit {

  private _songs: BehaviorSubject<Array<Song>> = new BehaviorSubject<Array<Song>>([]);
  playing: boolean = false;
  displayColumns: Array<string> = ['time', 'artist', 'title', 'length'];

  constructor(private http: HttpClient, private dragulaService: DragulaService) { }

  ngOnInit() {
  }

  playPause()
  {
    this.playing = !this.playing;
  }

  get songs(): Observable<Array<Song>> {
    return this._songs.asObservable();
  }

  isCurrentSong(index: number, item: Song) {
    return item == this._songs.getValue()[0];
  }

  playtime(song: Song) {
    var startTime: Date = null;
    this._songs.getValue().some(currentSong => {
      if (startTime == null)
      {
        startTime = currentSong.started;
      }
      if (currentSong == song) {
        return true;
      }
      startTime.setTime(startTime.getTime() + currentSong.length);
      return false;
    });
    return startTime;
  }

}
