import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { TopBarCustomComponent } from './top-bar-custom.component';

describe('TopBarCustomComponent', () => {
    let component: TopBarCustomComponent;
    let fixture: ComponentFixture<TopBarCustomComponent>;

    beforeEach(async(() => {
        TestBed.configureTestingModule({
            declarations: [TopBarCustomComponent]
        })
            .compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(TopBarCustomComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
