import { Component, OnInit } from '@angular/core';
import { ConfigService } from "../../config/config.service";

@Component({
    selector: 'app-page-not-found',
    templateUrl: './page-not-found.component.html',
    styleUrls: ['./page-not-found.component.css']
})
export class PageNotFoundComponent implements OnInit {

    constructor(
        private config: ConfigService
    ) { }

    ngOnInit() {
        this.config.setPageTitle("Page Not Found");
    }

}
