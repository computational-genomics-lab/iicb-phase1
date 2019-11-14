import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ScaffoldLinkDetailsComponent } from './scaffold-link-details.component';

describe('ScaffoldLinkDetailsComponent', () => {
  let component: ScaffoldLinkDetailsComponent;
  let fixture: ComponentFixture<ScaffoldLinkDetailsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ScaffoldLinkDetailsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ScaffoldLinkDetailsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
