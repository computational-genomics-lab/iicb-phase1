import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { NonCodingComponent } from './non-coding.component';

describe('NonCodingComponent', () => {
  let component: NonCodingComponent;
  let fixture: ComponentFixture<NonCodingComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ NonCodingComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(NonCodingComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
