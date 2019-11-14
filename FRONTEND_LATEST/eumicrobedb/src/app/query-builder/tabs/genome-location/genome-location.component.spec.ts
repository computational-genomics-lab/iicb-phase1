import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { GenomeLocationComponent } from './genome-location.component';

describe('GenomeLocationComponent', () => {
  let component: GenomeLocationComponent;
  let fixture: ComponentFixture<GenomeLocationComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ GenomeLocationComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(GenomeLocationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
