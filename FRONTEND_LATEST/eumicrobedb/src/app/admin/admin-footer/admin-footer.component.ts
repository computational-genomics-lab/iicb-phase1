import { Component, OnInit } from '@angular/core';
import { ConfigService } from "../../config/config.service";

@Component({
    selector: 'app-admin-footer',
    templateUrl: './admin-footer.component.html',
    styleUrls: ['./admin-footer.component.css']
})
export class AdminFooterComponent implements OnInit {
    companyName: string;
    curTime: Date;

    constructor(
        private config: ConfigService
    ) { }

    ngOnInit() {
        this.curTime = new Date();
        this.companyName = this.config.getSiteName();
    }

}
