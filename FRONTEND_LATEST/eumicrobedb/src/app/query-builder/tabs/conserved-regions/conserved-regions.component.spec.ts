import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ConservedRegionsComponent } from './conserved-regions.component';

describe('ConservedRegionsComponent', () => {
  let component: ConservedRegionsComponent;
  let fixture: ComponentFixture<ConservedRegionsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ConservedRegionsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ConservedRegionsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
