import { Component, OnInit, Input } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AvailableInputsService, AvailableInput } from '../available-inputs.service';
import { Observable } from 'rxjs/Observable';
import * as io from 'socket.io-client';

class Channel {
  constructor(public id: string, public input_id: string, public volume: number) { }
}

@Component({
  selector: 'app-mixer',
  templateUrl: './mixer.component.html',
  styleUrls: ['./mixer.component.css']
})
export class MixerComponent implements OnInit {

  // The ID of this mixer on the server
  @Input('input_id') id: string;
  // The display name of this mixer
  name: string;
  // The channels for this mixer
  channels: Array<Channel> = [];
  // The number of output channels
  output_channels: number;
  // All of the inputs available currently
  inputs: Observable<Array<AvailableInput>>;

  private socket: SocketIOClient.Socket;

  constructor(private http: HttpClient, private inputService: AvailableInputsService) {
    this.inputs = inputService.inputs;
  }

  ngOnInit() {
    this.socket = io();
    this.socket.on('mixer_channel_create', this.createMixerChannelEvent.bind(this));
    this.socket.on('mixer_channel_update', this.updateMixerChannelEvent.bind(this));
    this.socket.on('mixer_channel_remove', this.removeMixerChannelEvent.bind(this));
    this.http.get<Array<Channel>>('/audio/mixer/' + this.id).subscribe((data: any) => {
      this.name = data['display_name'];
      this.output_channels = data['output_channels'];
      let channels = this.channels;
      data['channels'].forEach(function (channel) {
        channels.push(new Channel(channel['id'], channel['input'], channel['volume']));
      });
    });
  }

  createMixerChannelEvent(data): void {
    if (data.mixer != this.id) {
      return;
    }
    if (!this.channels.some(x => x.id == data.channel)) {
      this.channels.push(new Channel(data.channel, '', 1.0));
    }
  }

  updateMixerChannelEvent(data): void {
    if (data.mixer != this.id) {
      return;
    }
    let channel = this.channels.find(x => x.id == data.channel);
    if ('volume' in data) {
      channel.volume = data.volume
    }
    if ('input' in data) {
      channel.input_id = data.input
    }
  }

  removeMixerChannelEvent(data): void {
    if (data.mixer != this.id) {
      return;
    }
    let channel = this.channels.find(x => x.id == data.channel);
    let index = this.channels.indexOf(channel, 0);
    if (index != -1) {
      this.channels.splice(index, 1);
    }
  }

  newChannel() {
    this.http.post<string>('/audio/mixer/' + this.id + '/channel', {}).subscribe();
  }

  changeInput(channel: Channel, input_id: string): void {
    let previous_id = channel.input_id;
    channel.input_id = input_id;
    this.http.put('/audio/mixer/' + this.id + '/channel/' + channel.id, {'input' : input_id}).subscribe(
      success => { },
      error => {
        channel.input_id = previous_id;
      }
    );
  }

  changeVolume(channel: Channel, volume: number): void {
    this.http.put('/audio/mixer/' + this.id + '/channel/' + channel.id, {'volume' : volume}).subscribe();
  }

  changeName(name: string): void {
    this.http.put('/audio/mixer/' + this.id, {'display_name': name}).subscribe();
  }

  removeChannel(channel: Channel): void {
    this.http.delete('/audio/mixer/' + this.id + '/channel/' + channel.id).subscribe();
  }

}
