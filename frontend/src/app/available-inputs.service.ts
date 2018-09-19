import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export class AvailableInput {
  constructor(public id: string, public name: string) { }
}

@Injectable({
  providedIn: 'root'
})
export class AvailableInputsService {
  private inputSubject: BehaviorSubject<Array<AvailableInput>> = new BehaviorSubject<Array<AvailableInput>>([]);
  private inputArray: Array<AvailableInput> = [];

  constructor() { }

  get inputs() {
    return this.inputSubject.asObservable();
  }

  addInput(id: string, name: string) {
    let found = false;
    this.inputArray.forEach((item: AvailableInput, index: number) => {
      if (item.id === id) {
        item.name = name;
        found = true;
      }
    });
    if (found == false) {
      this.inputArray.push(new AvailableInput(id, name));
      this.inputSubject.next(this.inputArray.slice());
    }
  }

  removeInput(id: string) {
    this.inputArray.forEach((item: AvailableInput, index: number) => {
      if(item.id === id) {
        this.inputArray.splice(index, 1);
      }
    });
    this.inputSubject.next(this.inputArray.slice());
  }

}
