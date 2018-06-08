import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { MixerListComponent } from './mixer-list.component';

describe('MixerListComponent', () => {
  let component: MixerListComponent;
  let fixture: ComponentFixture<MixerListComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ MixerListComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MixerListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
