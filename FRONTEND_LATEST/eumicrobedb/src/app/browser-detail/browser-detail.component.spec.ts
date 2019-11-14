import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { BrowserDetailComponent } from './browser-detail.component';

describe('BrowserDetailComponent', () => {
  let component: BrowserDetailComponent;
  let fixture: ComponentFixture<BrowserDetailComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ BrowserDetailComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(BrowserDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
