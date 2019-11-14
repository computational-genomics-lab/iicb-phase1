import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { DataUsagePolicyComponent } from './data-usage-policy.component';

describe('DataUsagePolicyComponent', () => {
  let component: DataUsagePolicyComponent;
  let fixture: ComponentFixture<DataUsagePolicyComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ DataUsagePolicyComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DataUsagePolicyComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
