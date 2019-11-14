import { Component, OnInit } from '@angular/core';

import { ConfigService } from "../config/config.service";

@Component({
    selector: 'app-sidebar-left',
    templateUrl: './sidebar-left.component.html',
    styleUrls: ['./sidebar-left.component.css']
})
export class SidebarLeftComponent implements OnInit {

    news_feed:any = [];
    videos_feed:any = [];

    constructor(
        private config: ConfigService 
    ) { }


    ngOnInit() {
       this.getWidgets();
    }


    getWidgets() {
        Promise.all( [  this.getNewsWidget(), this.getVideoTutorialsWidget() ] )
        .then(datas => {          
            this.news_feed   = datas[0];
            this.videos_feed = datas[1];
        });
    }    


    getNewsWidget() {
        return new Promise( (resolve, reject) => {
            fetch( this.config.getNews() )
            .then( data => data.json() )
            .then( res => { 
                let items = res.items;
                resolve( items.filter( (item: any) => item.Line_Status === 1 ) ) ;
            } )
            .catch( err => reject( err ) );
        } );
    } 
    
    
    getVideoTutorialsWidget() {
        return new Promise( (resolve, reject) => {
            fetch( this.config.getVideoTutorials() )
            .then( data => data.json() )
            .then( res => resolve( res.items.filter( (item: any) => item.video_status == 1 ) ) )
            .catch( err => reject( err ) );
        } );
    } 

}
