import { TestBed, inject } from '@angular/core/testing';

import { DirectoryPickerService } from './directory-picker.service';

describe('DirectoryPickerService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [DirectoryPickerService]
    });
  });

  it('should be created', inject([DirectoryPickerService], (service: DirectoryPickerService) => {
    expect(service).toBeTruthy();
  }));
});
