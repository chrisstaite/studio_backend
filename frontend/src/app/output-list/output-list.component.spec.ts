import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { OutputListComponent } from './output-list.component';

describe('OutputListComponent', () => {
  let component: OutputListComponent;
  let fixture: ComponentFixture<OutputListComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ OutputListComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(OutputListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
