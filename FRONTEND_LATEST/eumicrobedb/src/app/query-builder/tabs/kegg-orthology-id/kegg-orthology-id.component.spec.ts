import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { KeggOrthologyIdComponent } from './kegg-orthology-id.component';

describe('KeggOrthologyIdComponent', () => {
  let component: KeggOrthologyIdComponent;
  let fixture: ComponentFixture<KeggOrthologyIdComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ KeggOrthologyIdComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(KeggOrthologyIdComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
