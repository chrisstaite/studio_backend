import { Component, OnInit } from '@angular/core';
import * as io from 'socket.io-client';

class Output {

}

@Component({
  selector: 'app-output-list',
  templateUrl: './output-list.component.html',
  styleUrls: ['./output-list.component.css']
})
export class OutputListComponent implements OnInit {
  outputs: Array<Output>;
  private socket: SocketIOClient.Socket;

  constructor() { }

  ngOnInit() {
    this.socket = io()
  }

}
