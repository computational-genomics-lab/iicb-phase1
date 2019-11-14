import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';

import { AuthenticationService, DataSharingService, GnomeToolbox } from '../_services';

@Component({
    selector: 'app-top-bar-custom',
    templateUrl: './top-bar-custom.component.html',
    styleUrls: ['./top-bar-custom.component.css']
})
export class TopBarCustomComponent implements OnInit {

    isUserLoggedIn: boolean;    
    urlParams: any;

    constructor(
        private authenticationService: AuthenticationService,
        private router: Router,
        private route: ActivatedRoute,
        private dataSharingService: DataSharingService,
        private genomeTool: GnomeToolbox
    ) {
        this.dataSharingService.isUserLoggedIn.subscribe( value => {
            this.isUserLoggedIn = value;
        });          
    }

    ngOnInit() {        
        // Parse url params
        this.route
        .queryParams
        .subscribe(params => { 
            this.urlParams = params;
        });       
    }
    

    onLogout() {
        this.authenticationService.logout();
        this.router.navigate(['/login']);
    }


    moveLeft() {
        this.genomeTool.moveLeft();
    }


    moveRight() {
        this.genomeTool.moveRight();
    }


    prevScaffold() {
        this.genomeTool.movePrevScaffold();
    }


    nextScaffold() {
        this.genomeTool.moveNextScaffold();
    }

}
