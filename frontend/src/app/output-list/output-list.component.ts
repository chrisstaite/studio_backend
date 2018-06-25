import { Component, Inject, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { MatDialog, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material';
import { AvailableInputsService, AvailableInput } from '../available-inputs.service';
import { Observable } from 'rxjs/Observable';
import * as io from 'socket.io-client';

class Output {

  type: string;
  id: string;
  display_name: string;
  input_id: string;
  parameters: any;

  constructor() { }

  deserialise(input: any) {
    this.type = input['type'];
    delete input['type'];
    this.id = input['id'];
    delete input['id'];
    this.display_name = input['display_name'];
    delete input['display_name'];
    this.input_id = input['input_id'];
    delete input['input_id'];
    this.parameters = input;
    return this;
  }

}

@Component({
  selector: 'app-output-list',
  templateUrl: './output-list.component.html',
  styleUrls: ['./output-list.component.css']
})
export class OutputListComponent implements OnInit {
  outputs: Array<Output> = [];

  inputs: Observable<Array<AvailableInput>>;

  private socket: SocketIOClient.Socket;

  constructor(private http: HttpClient, private dialog: MatDialog, private inputService: AvailableInputsService) { }

  ngOnInit() {
    this.socket = io();
    this.inputs = this.inputService.inputs;
    let outputs = this.outputs;
    this.http.get<Array<Output>>('/audio/output').subscribe((data: Array<Output>) => {
      data.forEach(function (output) {
        outputs.push(new Output().deserialise(output));
      });
    });
  }

  newOutput(): void {
    this.dialog.open(NewOutputDialog, { data: { parent: this } });
  }

  removeOutput(output: Output): void {
    this.http.delete('/audio/output/' + output.id).subscribe(() => {
      let index = this.outputs.indexOf(output, 0);
      if (index > -1) {
         this.outputs.splice(index, 1);
      }
    });
  }

  changeName(output: Output, name: string): void {
    this.http.put('/audio/output/' + output.id, {'display_name' : name}).subscribe();
  }

  changeInput(output: Output, input_id: string): void {
    this.http.put('/audio/output/' + output.id, {'input' : input_id}).subscribe();
  }

}

@Component({
  templateUrl: './new-output-dialog.html',
  styleUrls: ['./new-output-dialog.css']
})
export class NewOutputDialog implements OnInit {

  public devices: Array<string> = [];
  public available_devices: Array<Output> = [];

  constructor(
    private http: HttpClient,
    private dialog: MatDialogRef<NewOutputDialog>,
    @Inject(MAT_DIALOG_DATA) private data: any)
  { }

  ngOnInit() {
    this.http.get<Array<string>>('/audio/output/devices').subscribe((data: Array<string>) => {
      this.devices = data;
    });
    this.data.parent.outputs.forEach((output: Output) => {
      if (output.type == 'device') {
        this.available_devices.push(output);
      }
    });
  }

  onNoClick(): void {
    this.dialog.close();
  }

  private newDeviceHandler(outputs: Array<Output>): void {
    outputs.forEach((output: Output) => {
      this.data.parent.outputs.push(new Output().deserialise(output));
    });
    this.dialog.close();
  }

  newOutputDevice(output_device: string): void {
    let new_device = { 'type': 'device', 'display_name': output_device, 'name': output_device };
    this.http.post<Array<Output>>('/audio/output', new_device).subscribe(this.newDeviceHandler.bind(this));
  }

  newMultiplex(parent: string, channels: string): void {
    let parent_name = 'Multiplexed';
    this.data.parent.outputs.forEach((output: Output) => {
      if (output.id == parent) {
        parent_name = output.display_name;
      }
    });
    let new_device = { 'type': 'multiplex', 'display_name': parent_name, 'parent_id': parent, 'channels': channels };
    this.http.post<Array<Output>>('/audio/output', new_device).subscribe(this.newDeviceHandler.bind(this));
  }

  newIcecast(endpoint: string, password: string): void {
    let new_device = { 'type': 'icecast', 'display_name': endpoint, 'endpoint': endpoint, 'password': password };
    this.http.post<Array<Output>>('/audio/output', new_device).subscribe(this.newDeviceHandler.bind(this));
  }

}
