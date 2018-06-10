import { Component, Inject, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { MatDialog, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material';
import * as io from 'socket.io-client';

class Input {

  type: string;
  id: string;
  display_name: string;
  parameters: any;

  constructor() { }

  deserialise(input: any) {
    this.type = input['type'];
    delete input['type'];
    this.id = input['id'];
    delete input['id'];
    this.display_name = input['display_name'];
    delete input['display_name'];
    this.parameters = input;
    return this;
  }

}

@Component({
  selector: 'app-input-list',
  templateUrl: './input-list.component.html',
  styleUrls: ['./input-list.component.css']
})
export class InputListComponent implements OnInit {
  inputs: Array<Input> = [];

  private socket: SocketIOClient.Socket;

  constructor(private http: HttpClient, private dialog: MatDialog) { }

  ngOnInit() {
    this.socket = io();
    // For some reason in this special case, this goes out of scope??
    let that = this;
    this.http.get<Array<Input>>('/audio/input').subscribe((data: Array<Input>) => {
      data.forEach(function (input) {
        that.inputs.push(new Input().deserialise(input));
      });
    });
  }

  newInput(): void {
    this.dialog.open(NewInputDialog, { data: { parent: this } });
  }

  removeInput(input: Input): void {
    this.http.delete('/audio/input/' + input.id).subscribe(() => {
      let index = this.inputs.indexOf(input, 0);
      if (index > -1) {
         this.inputs.splice(index, 1);
      }
    });
  }

}

@Component({
  templateUrl: './new-input-dialog.html',
  styleUrls: ['./new-input-dialog.css']
})
export class NewInputDialog implements OnInit {

  public devices: Array<string> = [];

  constructor(
    private http: HttpClient,
    private dialog: MatDialogRef<NewInputDialog>,
    @Inject(MAT_DIALOG_DATA) private data: any)
  { }

  ngOnInit() {
    this.http.get<Array<string>>('/audio/input/devices').subscribe((data: Array<string>) => {
      this.devices = data;
    });
  }

  onNoClick(): void {
    this.dialog.close();
  }

  private newDeviceHandler(inputs: Array<Input>): void {
    inputs.forEach((input: Input) => {
      this.data.parent.inputs.push(new Input().deserialise(input));
    });
    this.dialog.close();
  }

  newInputDevice(input_device: string): void {
    let new_device = { 'type': 'device', 'display_name': input_device, 'name': input_device };
    this.http.post<Array<Input>>('/audio/input', new_device).subscribe(this.newDeviceHandler.bind(this));
  }

}
