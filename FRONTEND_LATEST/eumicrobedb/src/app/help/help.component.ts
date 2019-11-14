import { Component, OnInit } from '@angular/core';

import { ConfigService } from '../config/config.service';
import { DataSharingService } from 'src/app/_services';

@Component({
    selector: 'app-help',
    templateUrl: './help.component.html',
    styleUrls: ['./help.component.css']
})
export class HelpComponent implements OnInit {
    helpTop: any;
    helpBottom: any;

    constructor(
        private config: ConfigService,
        private ds: DataSharingService
    ) { }

    ngOnInit() {
        this.config.setPageTitle("Help");

        this.getHelpCombined();
    }

    getHelpCombined() {
        Promise.all( [  this.getHelp(), this.getHelpQA() ] )
        .then(datas => {
            this.helpTop    = datas[0];
            this.helpBottom = datas[1];
        });        
    }


    getHelp() {
        return new Promise( (resolve, reject) => {
            fetch( this.config.getHelpPage() )
            .then( data => data.json() )
            .then( res => { 
                let items = res.lines.filter( (item: any) => item.Help_Status === 1 );
                resolve( items[0] ) ;
            } )
            .catch( err => reject( err ) );
        } );        
    }


    getHelpQA() {
        return new Promise( (resolve, reject) => {
            fetch( this.config.getHelpQAPage() )
            .then( data => data.json() )
            .then( res => { 
                let items = [];
                                
                for(let key in res.items) {
                    if(res.items[key].Status === 1) {
                        items.push(res.items[key]);
                    }
                }

                resolve( items ) ;
            } )
            .catch( err => reject( err ) );
        } );          
    }

}
