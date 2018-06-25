import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-browser-playback',
  templateUrl: './browser-playback.component.html',
  styleUrls: ['./browser-playback.component.css']
})
export class BrowserPlaybackComponent implements OnInit {

  playing: Boolean = false;

  private browserOutput: any = null;

  constructor() { }

  ngOnInit() {
    this.play();
  }

  play(): void {
    if (this.browserOutput == null) {
      this.browserOutput = new Audio();
      this.browserOutput.src = '/audio/output_stream/Browser';
      this.browserOutput.load();
    }

    let promise = this.browserOutput.play();
    if (promise !== undefined) {
      promise.then(_ => {
        this.playing = true;
      }).catch(error => {
        this.playing = false;
      });
    }
  }

  pause(): void {
    this.browserOutput.pause();
    this.browserOutput = null;
    this.playing = false;
  }

  handleClick() : void {
    if (this.playing == false) {
      this.play();
    }
  }

}
