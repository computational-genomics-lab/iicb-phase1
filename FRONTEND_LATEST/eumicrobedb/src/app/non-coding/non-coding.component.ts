import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';

import { ConfigService } from '../config';
import { DataSharingService } from 'src/app/_services';

@Component({
    selector: 'app-non-coding',
    templateUrl: './non-coding.component.html',
    styleUrls: ['./non-coding.component.css']
})
export class NonCodingComponent implements OnInit {
    
    loading: boolean = true;
    urlParams: any;
    data: any;

    constructor(
        private http: HttpClient,
        private route: ActivatedRoute, 
        private config: ConfigService,
        private router: Router,
        private ds: DataSharingService
    ) { }


    ngOnInit() {
        this.config.setPageTitle( "Genome Similarity Track Page" );

        this.route
        .queryParams
        .subscribe(params => { 
            this.urlParams = params;
            


            this.ds.postApiData(this.config.getNonCodingUrl(), this.urlParams)
            .then((resp:any) => {
                this.loading = false;
                this.data = resp;
            })
            .catch(err => this.loading = false);              

            // this.http.post(this.config.getNonCodingUrl(), this.urlParams, {
            //     responseType: "json"
            // })
            // .subscribe( (resp: any) => {
            //     this.loading = false;
            //     this.data = resp;
            // } );
        } );        
    }


    goToBrowserDetail( data ) {
        this.router.navigate( ['browser-detail'], { queryParams: data } )
    }

}
