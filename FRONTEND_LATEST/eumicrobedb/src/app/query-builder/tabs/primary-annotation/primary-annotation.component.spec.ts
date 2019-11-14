import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PrimaryAnnotationComponent } from './primary-annotation.component';

describe('PrimaryAnnotationComponent', () => {
  let component: PrimaryAnnotationComponent;
  let fixture: ComponentFixture<PrimaryAnnotationComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PrimaryAnnotationComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PrimaryAnnotationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
