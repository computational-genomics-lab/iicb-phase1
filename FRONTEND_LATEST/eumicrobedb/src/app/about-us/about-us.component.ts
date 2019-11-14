import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { ConfigService } from '../config/config.service';
import { DataSharingService } from 'src/app/_services';
import { Items } from '../_models';

@Component({
    selector: 'app-about-us',
    templateUrl: './about-us.component.html',
    styleUrls: ['./about-us.component.css']
})
export class AboutUsComponent implements OnInit {
    principal_investigator = [];
    graduate_students = [];
    masters_students = [];
    loading:boolean = true;
    defaultFolder = this.config.getMediaUrl().aboutUs;
    img_placeholder = 'https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y&s=200';
    timestamp = Date.now();

    constructor(
        private config: ConfigService,
        private http: HttpClient,
        private ds: DataSharingService
    ) { }

    ngOnInit() {
        this.config.setPageTitle('About Us');

        this.ds.getApiData(this.config.getAboutPage())
        .then((data: Items) => {
            if ( data.items ) {
                const members = data.items.filter( (item:any) => item.AboutUs_Status === 1 );

                members.forEach( (item:any) => {
                    switch ( item.AboutUs_Type_No ) {
                        case 1: this.principal_investigator.push( item );
                                break;
                        case 2: this.graduate_students.push( item );
                                break;
                        case 3: this.masters_students.push( item );
                                break;
                    }
                } );
            }
            this.loading = false;
        })
        .catch(err => this.loading = false);        

        // this.http.get<Items>( this.config.getAboutPage() )
        // .subscribe( (data: any) => {          
        //     if ( data.items ) {
        //         const members = data.items.filter( item => item.AboutUs_Status === 1 );

        //         members.forEach( item => {
        //             switch ( item.AboutUs_Type_No ) {
        //                 case 1: this.principal_investigator.push( item );
        //                         break;
        //                 case 2: this.graduate_students.push( item );
        //                         break;
        //                 case 3: this.masters_students.push( item );
        //                         break;
        //             }
        //         } );
        //     }
        //     this.loading = false;
        // } );
    }

}
