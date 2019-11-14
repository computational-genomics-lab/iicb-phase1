import { Injectable } from '@angular/core';
import { BehaviorSubject, Subject } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class QueryBuilderService {

    private listItems = new BehaviorSubject('');
    listData = this.listItems.asObservable();
    
    private queryStr = new Subject();
    queryData = this.queryStr.asObservable();

    private queryTabNo = new Subject();
    queryTab = this.queryTabNo.asObservable();


    getListItems( data: any ) {
        this.listItems.next( data );
    }
    

    getQuery( queryStr: any ) {
        this.queryStr.next( queryStr );
    }

    
    switchTab( tabNo: number ) {
        this.queryTabNo.next( tabNo );
    }
}