import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {

  ngOnInit() {
    let browserOutput = new Audio();
    browserOutput.src = '/audio/output_stream/Browser';
    browserOutput.load();
    browserOutput.play();
  }

}
