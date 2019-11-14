import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { ConfigService } from '../config/config.service';
import { DataSharingService } from 'src/app/_services';
import { Items } from '../_models';

@Component({
    selector: 'app-archive',
    templateUrl: './archive.component.html',
    styleUrls: ['./archive.component.css']
})
export class ArchiveComponent implements OnInit {
    loading: boolean = true;
    data: any;

    constructor(
        private config: ConfigService,
        private http: HttpClient,
        private ds: DataSharingService        
    ) { }

    ngOnInit() {
        this.config.setPageTitle('Archive');

        this.ds.getApiData(this.config.getArchivePage())
        .then((data:any) => {
            this.data = data.items.reverse().filter( item =>  item.Archive_Status === 1 );
            this.loading = false;
        })
        .catch(err => this.loading = false);          

        // this.http.get<Items>( this.config.getArchivePage() )
        // .subscribe( (data: any) => {
        //     this.data = data.items.reverse().filter( item =>  item.Archive_Status === 1 );
        //     this.loading = false;
        // } );        
    }

}
