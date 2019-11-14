import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';


@Component({
    selector: 'app-dashboard',
    templateUrl: './dashboard.component.html',
    styleUrls: ['./dashboard.component.css']
})

export class DashboardComponent implements OnInit {
    
    contentBlocks: any = [
        {
            "block": "Data Usage Policy Widget",
            "action": "editDataUsageBlock"
        },       
        {
            "block": "News Widget",
            "action": "editNewsBlock"
        },       
        {
            "block": "About Us Widget",
            "action": "editAboutBlock"
        },       
        {
            "block": "About Us Page",
            "action": "editAboutPage"
        },       
        {
            "block": "Help Page",
            "action": "editHelpPage"
        },
        {
            "block": "Help Q&A Page",
            "action": "editHelpQAPage"
        },
        {
            "block": "Archive Page",
            "action": "archivePage"
        },
        {
            "block": "Video Tutorials Widget",
            "action": "videoTutorialBlock"
        },
        {
            "block": "Contact Us Page",
            "action": "contactUsPage"
        }      
    ];

    constructor(
        private router: Router        
    ) { }

    ngOnInit() {
    }

    editBlock( block: any ) {
        switch( block.action ) {
            case "editDataUsageBlock": 
                this.router.navigate( ['/admin/block/data-usage-policy'], { queryParams: block } );
                break;

            case "editNewsBlock": 
                this.router.navigate( ['/admin/block/news'], { queryParams: block } );
                break;
            
            case "editAboutBlock": 
                this.router.navigate( ['/admin/block/about'], { queryParams: block } );
                break;

            case "editAboutPage": 
                this.router.navigate( ['/admin/page/about'], { queryParams: block } );
                break;

            case "editHelpPage": 
                this.router.navigate( ['/admin/page/help'], { queryParams: block } );
                break;
            
            case "editHelpQAPage": 
                this.router.navigate( ['/admin/page/help-qa'], { queryParams: block } );
                break;
            
            case "archivePage": 
                this.router.navigate( ['/admin/page/archive'], { queryParams: block } );
                break;
            
            case "videoTutorialBlock": 
                this.router.navigate( ['/admin/block/video-tutorials'], { queryParams: block } );
                break;

            case "contactUsPage": 
                this.router.navigate( ['/admin/page/contact-us'], { queryParams: block } );
                break;
        }        
    }

}
