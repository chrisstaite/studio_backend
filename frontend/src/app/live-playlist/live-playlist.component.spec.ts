import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { LivePlaylistComponent } from './live-playlist.component';

describe('LivePlaylistComponent', () => {
  let component: LivePlaylistComponent;
  let fixture: ComponentFixture<LivePlaylistComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ LivePlaylistComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(LivePlaylistComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
