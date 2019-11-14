import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';

import { ConfigService } from 'src/app/config';
import { DataSharingService } from 'src/app/_services';

@Component({
    selector: 'app-scaffold-link-details',
    templateUrl: './scaffold-link-details.component.html',
    styleUrls: ['./scaffold-link-details.component.css']
})
export class ScaffoldLinkDetailsComponent implements OnInit {

    loading: boolean = true;
    urlParams: any;
    data: any;    

    constructor(
        private http: HttpClient,
        private route: ActivatedRoute, 
        private config: ConfigService,
        private ds: DataSharingService
    ) { }


    ngOnInit() {
        this.config.setPageTitle( "Browser Detail" );

        this.route
        .queryParams
        .subscribe(params => { 
            this.urlParams = params;
            
            // Make a post request
            this.ds.postApiData(this.config.getScaffoldDetailUrl(), this.urlParams)
            .then((resp:any) => {
                this.loading = false;
                this.data = resp;
            })
            .catch(err => this.loading = false); 

            // this.http.post(this.config.getScaffoldDetailUrl(), this.urlParams, {
            //     responseType: "json"
            // })
            // .subscribe( (resp: any) => {
            //     this.loading = false;
            //     this.data = resp;
            // } );
        } );        
    }

}
