import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { GffTemplateComponent } from './gff-template.component';

describe('GffTemplateComponent', () => {
  let component: GffTemplateComponent;
  let fixture: ComponentFixture<GffTemplateComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ GffTemplateComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(GffTemplateComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
