import { TestBed, inject } from '@angular/core/testing';

import { AvailableInputsService } from './available-inputs.service';

describe('AvailableInputsService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [AvailableInputsService]
    });
  });

  it('should be created', inject([AvailableInputsService], (service: AvailableInputsService) => {
    expect(service).toBeTruthy();
  }));
});
