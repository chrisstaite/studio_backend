import { Component, OnInit, Input } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AvailableInputsService, AvailableInput } from '../available-inputs.service';
import { Observable } from 'rxjs/Observable';

class Channel {
  constructor(public input_id: string, public volume: number) { }
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

  constructor(private http: HttpClient, private inputService: AvailableInputsService) {
    this.inputs = inputService.inputs;
  }

  ngOnInit() {
    this.http.get<Array<Channel>>('/audio/mixer/' + this.id).subscribe((data: any) => {
      this.name = data['display_name'];
      this.output_channels = data['output_channels'];
      let channels = this.channels;
      data['channels'].forEach(function (channel) {
        channels.push(new Channel(channel['input'], channel['volume']));
      });
    });
  }

  newChannel() {
    let new_channel = { 'display_name': 'New Mixer', 'channels': 2 };
    let channels = this.channels;
    this.http.post<number>('/audio/mixer/' + this.id + '/channel', new_channel).subscribe((index: number) => {
      channels.push(new Channel('', 1.0));
    });
  }

  changeInput(channel: Channel, input_id: string): void {
    var channelId = this.channels.indexOf(channel);
    this.http.put('/audio/mixer/' + this.id + '/channel/' + channelId, {'input' : input_id}).subscribe();
  }

  changeVolume(channel: Channel, volume: number): void {
    var channelId = this.channels.indexOf(channel);
    this.http.put('/audio/mixer/' + this.id + '/channel/' + channelId, {'volume' : volume}).subscribe();
  }

}
