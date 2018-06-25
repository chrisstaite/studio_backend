import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AvailableInputsService } from '../available-inputs.service';

class Mixer {

  constructor(public id: string,
              public display_name: string,
              public output_channels: number,
              public channel_count: number) {
  }

}

@Component({
  selector: 'app-mixer-list',
  templateUrl: './mixer-list.component.html',
  styleUrls: ['./mixer-list.component.css']
})
export class MixerListComponent implements OnInit {
  mixers: Array<Mixer> = [];

  constructor(private http: HttpClient, private inputService: AvailableInputsService) { }

  ngOnInit() {
    let mixers = this.mixers;
    let inputService = this.inputService;
    this.http.get<Array<Mixer>>('/audio/mixer').subscribe((data: Array<Mixer>) => {
      data.forEach(function (mixer) {
        mixers.push(new Mixer(
          mixer['id'],
          mixer['display_name'],
          mixer['output_channels'],
          mixer['channel_count']
        ));
        inputService.addInput(mixer['id'], mixer['display_name']);
      });
    });
  }

  private newMixerHandler(data: Array<Mixer>): void {
    let mixers = this.mixers;
    let inputService = this.inputService;
    data.forEach(function (mixer) {
      mixers.push(new Mixer(
        mixer['id'],
        mixer['display_name'],
        mixer['output_channels'],
        mixer['channel_count']
      ));
      inputService.addInput(mixer['id'], mixer['display_name']);
    });
  }

  newMixer() {
    let new_mixer = { 'display_name': 'New Mixer', 'channels': 2 };
    this.http.post<Array<Mixer>>('/audio/mixer', new_mixer).subscribe(this.newMixerHandler.bind(this));
  }

}
