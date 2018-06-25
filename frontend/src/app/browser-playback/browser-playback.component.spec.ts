import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { BrowserPlaybackComponent } from './browser-playback.component';

describe('BrowserPlaybackComponent', () => {
  let component: BrowserPlaybackComponent;
  let fixture: ComponentFixture<BrowserPlaybackComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ BrowserPlaybackComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(BrowserPlaybackComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
