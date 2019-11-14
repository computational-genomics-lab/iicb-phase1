import { Component, OnInit } from '@angular/core';
import { AuthenticationService } from '../../_services';
import { Router } from '@angular/router';
import { BsDropdownModule } from 'ngx-bootstrap/dropdown';

@Component({
    selector: 'app-admin-header',
    templateUrl: './admin-header.component.html',
    styleUrls: ['./admin-header.component.css']
})
export class AdminHeaderComponent implements OnInit {

    constructor(
        private authenticationService: AuthenticationService,
        private router: Router
    ) { }

    ngOnInit(
        
    ) {
    }

    onLogout() {
        this.authenticationService.logout();
        this.router.navigate(['/login']);
    }    

}
