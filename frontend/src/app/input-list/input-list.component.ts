import { Component, Inject, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { MatDialog, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material';
import { AvailableInputsService } from '../available-inputs.service';
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

  constructor(private http: HttpClient, private dialog: MatDialog, private inputService: AvailableInputsService) { }

  ngOnInit() {
    this.socket = io();
    this.socket.on('input_create', this.createInputEvent.bind(this));
    this.socket.on('input_update', this.updateInputEvent.bind(this));
    this.socket.on('input_remove', this.removeInputEvent.bind(this));
    let that = this;
    this.http.get<Array<Input>>('/audio/input').subscribe((data: Array<Input>) => {
      data.forEach(function (input) {
        let new_input = new Input().deserialise(input);
        that.inputs.push(new_input);
        that.inputService.addInput(new_input.id, new_input.display_name);
      });
    });
  }

  createInputEvent(data: Array<Input>): void {
    let inputs = this.inputs;
    let inputService = this.inputService;
    data.forEach(function (input) {
      input = new Input().deserialise(input);
      if (!inputs.some(x => x.id == input.id)) {
        inputs.push(input);
        inputService.addInput(input.id, input.display_name);
      }
    });
  }

  updateInputEvent(data): void {
    let input = this.inputs.find(x => x.id == data.id);
    if ('display_name' in data) {
      input.display_name = data.display_name
    }
  }

  removeInputEvent(data): void {
    let input = this.inputs.find(x => x.id == data.id);
    let index = this.inputs.indexOf(input, 0);
    if (index != -1) {
      this.inputs.splice(index, 1);
    }
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
      this.inputService.removeInput(input.id);
    });
  }

  changeName(input: Input, name: string): void {
    this.http.put('/audio/input/' + input.id, {'display_name': name}).subscribe();
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
    @Inject(MAT_DIALOG_DATA) private data: any,
    private inputService: AvailableInputsService)
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
    this.dialog.close();
  }

  newInputDevice(input_device: string): void {
    let new_device = { 'type': 'device', 'display_name': input_device, 'name': input_device };
    this.http.post<Array<Input>>('/audio/input', new_device).subscribe(this.newDeviceHandler.bind(this));
  }

}
