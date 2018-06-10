import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  host: {
    '(document:click)': 'handleClick()',
  },
})
export class AppComponent implements OnInit {

  private browserOutput: any;
  private playing: Boolean;

  ngOnInit() {
    this.browserOutput = new Audio();
    this.browserOutput.src = '/audio/output_stream/Browser';
    this.browserOutput.load();
    this.play();
  }

  play() : void {
    let promise = this.browserOutput.play();
    if (promise !== undefined) {
      promise.then(_ => {
        this.playing = true;
      });
    }
  }

  handleClick() : void {
    if (this.playing == false) {
      this.play();
    }
  }

}
