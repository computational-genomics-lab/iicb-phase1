import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SecretomeComponent } from './secretome.component';

describe('SecretomeComponent', () => {
  let component: SecretomeComponent;
  let fixture: ComponentFixture<SecretomeComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SecretomeComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SecretomeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
