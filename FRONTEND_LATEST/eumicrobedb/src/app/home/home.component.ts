import { Component, OnInit } from '@angular/core';
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

import { ConfigService } from "../config/config.service";
import { DataSharingService } from 'src/app/_services';
import { error } from '@angular/compiler/src/util';


@Component({
    selector: 'app-home',
    templateUrl: './home.component.html',
    styleUrls: [
        './home.component.css',
        '../../assets/css/tab.css'
    ]
})

@Injectable()

export class HomeComponent implements OnInit {

    loading: boolean = true;
    treeItems = [];
    listItems = [];   

    constructor( 
        private http: HttpClient, 
        private router: Router, 
        private config: ConfigService,     
        private ds: DataSharingService   
    ) { }

    ngOnInit() {
        this.config.setPageTitle( "Home" );       

        // fetch tree view
        this.ds.getApiData(this.config.getapiTreeUrl())
        .then((resp:any) => {
            this.loading = false;
            if (resp['List']) {
                this.treeItems = resp['List'];
            }
        })
        .catch(err => this.loading = false);

        // this.http.get(this.config.getapiTreeUrl(), {
        //     responseType: "json"
        // })
        // .subscribe((resp) => {
        //     this.loading = false;
        //     if (resp['List']) {
        //         this.treeItems = resp['List'];
        //     }
        // }, error => {
        //     console.log(error);
        // });

        // fetch list view
        this.ds.getApiData(this.config.getapiListUrl())
        .then((resp:any) => {
            this.loading = false;
            if (resp['List']) {
                this.listItems = resp['List'];
            }
        })
        .catch(err => this.loading = false);

        // this.http.get(this.config.getapiListUrl(), {
        //     responseType: "json"
        // })
        // .subscribe((resp) => {
        //     this.loading = false;
        //     if (resp['List']) {
        //         this.listItems = resp['List'];
        //     }
        // }, error => {
        //     console.log(error);
        // });
    }

    viewList( item: object ) {
        this.router.navigate( ['/genome-viewer'], { queryParams: item } );
    }


    toggleChild( item: any ) {
        let id = item.target.dataset.id;

        item.target.previousElementSibling.classList.toggle("fa-plus-square");
        item.target.previousElementSibling.classList.toggle("fa-minus-square");
        document.getElementById( id ).classList.toggle("d-none");
    }
    
    toggleiChild( item: any ) {
        let id = item.target.dataset.id;

        item.target.classList.toggle("fa-plus-square");
        item.target.classList.toggle("fa-minus-square");
        document.getElementById( id ).classList.toggle("d-none");
    }


    toggleTab(event: { target: { dataset: { show: string; }; classList: { add: (arg0: string) => void; }; }; }) {
        if (event.target.dataset.show === "0") {
            document.querySelector(".tab-horiz .tab-content").lastElementChild.classList.add("d-none");
            document.querySelector(".tab-horiz .tab-content").firstElementChild.classList.remove("d-none");
            document.querySelectorAll(".tab-legend li").forEach(item => item.classList.remove("active"));
        } else {
            document.querySelector(".tab-horiz .tab-content").firstElementChild.classList.add("d-none");
            document.querySelector(".tab-horiz .tab-content").lastElementChild.classList.remove("d-none");
            document.querySelectorAll(".tab-legend li").forEach(item => item.classList.remove("active"))
        }
        event.target.classList.add("active");
    }

}
