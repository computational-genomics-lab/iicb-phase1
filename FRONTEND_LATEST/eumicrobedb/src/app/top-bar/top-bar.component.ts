import { Component, OnInit } from '@angular/core';
import { AuthenticationService, DataSharingService } from '../_services';
import { Router } from '@angular/router';

@Component({
    selector: 'app-top-bar',
    templateUrl: './top-bar.component.html',
    styleUrls: ['./top-bar.component.css']
})
export class TopBarComponent implements OnInit {

    isUserLoggedIn: boolean;

    constructor(
        private authenticationService: AuthenticationService,
        private router: Router,
        private dataSharingService: DataSharingService  
    ) {
        this.dataSharingService.isUserLoggedIn.subscribe( value => {
            this.isUserLoggedIn = value;
        });        
    }

    ngOnInit() {        
       
    }

    onLogout() {
        this.authenticationService.logout();
        this.router.navigate(['/login']);
    }

}
