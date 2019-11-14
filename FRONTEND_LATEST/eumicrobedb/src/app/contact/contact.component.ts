import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { ConfigService } from '../config/config.service';
import { DataSharingService } from 'src/app/_services';
import { Items } from '../_models';

@Component({
    selector: 'app-contact',
    templateUrl: './contact.component.html',
    styleUrls: ['./contact.component.css']
})
export class ContactComponent implements OnInit {
    loading: boolean = true;
    data: any;

    constructor(
        private config: ConfigService,
        private http: HttpClient,
        private ds: DataSharingService
    ) { }

    ngOnInit() {
        this.config.setPageTitle("Contact");

        this.ds.getApiData(this.config.getContactPage())
        .then((data:any) => {
            this.data = data.items.filter( item =>  item.ContactUs_Status == 1 );
            this.loading = false;
        })
        .catch(err => this.loading = false);        

        // this.http.get<Items>( this.config.getContactPage() )
        // .subscribe( (data: any) => {
        //     this.data = data.items.filter( item =>  item.ContactUs_Status == 1 );
        //     this.loading = false;
        // } ); 
    }

}
