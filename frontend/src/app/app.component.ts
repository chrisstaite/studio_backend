import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {

  ngOnInit() {
    /*  Can't do this for two reasons:
      - Blocking IO causes the server to lock up, need to fix eventlet
      - Chrome doesn't allow auto-play anymore
    let browserOutput = new Audio();
    browserOutput.src = '/audio/output_stream/Browser';
    browserOutput.load();
    browserOutput.play();
    */
  }

}
