import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AvailableInputsService } from '../available-inputs.service';
import * as io from 'socket.io-client';

class Mixer {

  constructor(public id: string,
              public display_name: string,
              public output_channels: number) {
  }

}

@Component({
  selector: 'app-mixer-list',
  templateUrl: './mixer-list.component.html',
  styleUrls: ['./mixer-list.component.css']
})
export class MixerListComponent implements OnInit {
  mixers: Array<Mixer> = [];

  private socket: SocketIOClient.Socket;

  constructor(private http: HttpClient, private inputService: AvailableInputsService) { }

  ngOnInit() {
    this.socket = io();
    this.socket.on('mixer_create', this.createMixerEvent.bind(this));
    this.socket.on('mixer_update', this.updateMixerEvent.bind(this));
    this.socket.on('mixer_remove', this.removeMixerEvent.bind(this));
    let mixers = this.mixers;
    let inputService = this.inputService;
    this.http.get<Array<Mixer>>('/audio/mixer').subscribe((data: Array<Mixer>) => {
      data.forEach(function (mixer) {
        mixers.push(new Mixer(
          mixer['id'],
          mixer['display_name'],
          mixer['output_channels']
        ));
        inputService.addInput(mixer['id'], mixer['display_name']);
      });
    });
  }

  createMixerEvent(data: Array<Mixer>): void {
    let mixers = this.mixers;
    let inputService = this.inputService;
    data.forEach(function (mixer) {
      mixer = new Mixer(mixer['id'], mixer['display_name'], mixer['output_channels']);
      if (!mixers.some(x => x.id == mixer.id)) {
        mixers.push(mixer);
        inputService.addInput(mixer.id, mixer.display_name);
      }
    });
  }

  updateMixerEvent(data): void {
    let mixer = this.mixers.find(x => x.id == data.id);
    if ('display_name' in data) {
      mixer.display_name = data.display_name
    }
  }

  removeMixerEvent(data): void {
    let mixer = this.mixers.find(x => x.id == data.id);
    let index = this.mixers.indexOf(mixer, 0);
    if (index != -1) {
      this.mixers.splice(index, 1);
    }
  }

  newMixer() {
    let new_mixer = { 'display_name': 'New Mixer', 'channels': 2 };
    this.http.post<Array<Mixer>>('/audio/mixer', new_mixer).subscribe();
  }

}
