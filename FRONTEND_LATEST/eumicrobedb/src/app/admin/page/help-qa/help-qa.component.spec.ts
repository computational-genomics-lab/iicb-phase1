import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { HelpQaComponent } from './help-qa.component';

describe('HelpQaComponent', () => {
  let component: HelpQaComponent;
  let fixture: ComponentFixture<HelpQaComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ HelpQaComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(HelpQaComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
