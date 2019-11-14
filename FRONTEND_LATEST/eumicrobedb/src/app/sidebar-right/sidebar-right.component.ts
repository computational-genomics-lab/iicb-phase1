import { Component, OnInit } from '@angular/core';

import { ConfigService } from "../config/config.service";

@Component({
    selector: 'app-sidebar-right',
    templateUrl: './sidebar-right.component.html',
    styleUrls: ['./sidebar-right.component.css']
})
export class SidebarRightComponent implements OnInit {

    about_feed:any = "";
    usage_feed:any = [];    

    constructor(
        private config: ConfigService
    ) { }

    ngOnInit() {
        this.getWidgets();
    }

    getWidgets() {
        Promise.all( [  this.getAboutWidget(), this.getUsagePolicyWidget() ] )
        .then(datas => {            
            this.about_feed = datas[0];
            this.usage_feed = datas[1];
        });
    }
    
    getAboutWidget() {
        return new Promise( (resolve, reject) => {
            fetch( this.config.getAbout() )
            .then( data => data.json() )
            .then( res => resolve( res.items.map( item => item.About_Text ).join("<br/>") ) )
            .catch( err => reject( err ) );
        } );
    }

    getUsagePolicyWidget() {
        return new Promise( (resolve, reject) => {
            fetch( this.config.getDataUsagePolicy() )
            .then( data => data.json() )
            .then( res => resolve( res.lines ) )
            .catch( err => reject( err ) );
        } );
    }    

}
