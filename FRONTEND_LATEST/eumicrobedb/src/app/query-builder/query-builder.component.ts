import { Component, OnInit, ViewChild } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { ConfigService } from 'src/app/config';
import { QueryBuilderService, DataSharingService } from 'src/app/_services';

@Component({
    selector: 'app-query-builder',
    templateUrl: './query-builder.component.html',
    styleUrls: ['./query-builder.component.css']
})
export class QueryBuilderComponent implements OnInit {
    listItems: any = [];

    constructor(
        private http: HttpClient,
        private config: ConfigService,
        private qbService: QueryBuilderService,
        private ds: DataSharingService
    ) {}

    
    ngOnInit() {
        // fetch list view
        this.ds.getApiData(this.config.getapiListUrl())
        .then((resp:any) => {
            if (resp['List']) {
                this.qbService.getListItems( resp['List'] );
            }
        })
        .catch(err => console.log(err));

        // this.http.get(this.config.getapiListUrl(), {
        //     responseType: "json"
        // })
        // .subscribe((resp) => {
        //     if (resp['List']) {
        //         this.qbService.getListItems( resp['List'] );
        //     }
        // });    
        

        // Recieving switch tab command
        this.qbService.queryTab.subscribe((tabNo: number) => {
            if( tabNo < 10 ) {
                this.switchTabByNo( tabNo );
            }
        });        
    }


    switchTab( event: Event ) {
        const item = <HTMLAnchorElement> event.target;
        const tabId = item.attributes['aria-controls'].value;

        document.querySelectorAll(".nav-tabs--vertical .nav-link").forEach( elem => elem.classList.remove("active") );
        document.querySelector(`[aria-controls="${tabId}"]`).classList.add("active");

        document.querySelectorAll(".tab-pane").forEach( elem => elem.classList.remove("show", "active") );
        document.getElementById(tabId).classList.add("show", "active");
    }


    switchTabByNo( tabNo: number ) {
        let item = <HTMLAnchorElement> document.querySelector(`.nav-tabs--left li:nth-child(${tabNo}) a`);
        const tabId = item.attributes['aria-controls'].value;

        document.querySelectorAll(".nav-tabs--vertical .nav-link").forEach( elem => elem.classList.remove("active") );
        document.querySelector(`[aria-controls="${tabId}"]`).classList.add("active");

        document.querySelectorAll(".tab-pane").forEach( elem => elem.classList.remove("show", "active") );
        document.getElementById(tabId).classList.add("show", "active");
    }

}
