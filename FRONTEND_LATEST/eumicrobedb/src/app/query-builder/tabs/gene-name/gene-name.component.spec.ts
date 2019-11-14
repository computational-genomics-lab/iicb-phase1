import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { GeneNameComponent } from './gene-name.component';

describe('GeneNameComponent', () => {
  let component: GeneNameComponent;
  let fixture: ComponentFixture<GeneNameComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ GeneNameComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(GeneNameComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
