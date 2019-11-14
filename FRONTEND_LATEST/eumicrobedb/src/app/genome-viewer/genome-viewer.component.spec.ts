import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { GenomeViewerComponent } from './genome-viewer.component';

describe('GenomeViewerComponent', () => {
  let component: GenomeViewerComponent;
  let fixture: ComponentFixture<GenomeViewerComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ GenomeViewerComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(GenomeViewerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
