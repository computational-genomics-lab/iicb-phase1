import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class GnomeToolbox {

    // Observable string sources
    private btnMoveLeft = new Subject<string>();
    private btnMoveRight = new Subject<string>();
    private btnScaffoldLeft = new Subject<string>();
    private btnScaffoldRight = new Subject<string>();

    // Observable string streams
    btnMoveLeftAction$ = this.btnMoveLeft.asObservable();
    btnMoveRightAction$ = this.btnMoveRight.asObservable();
    btnScaffoldLeftAction$ = this.btnScaffoldLeft.asObservable();
    btnScaffoldRightAction$ = this.btnScaffoldRight.asObservable();


    // Service message commands
    moveLeft() {
        this.btnMoveLeft.next();
    }
    

    moveRight() {
        this.btnMoveRight.next();
    }


    movePrevScaffold() {
        this.btnScaffoldLeft.next();
    }
    

    moveNextScaffold() {
        this.btnScaffoldRight.next();
    }
}