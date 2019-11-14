import { Component, OnInit } from '@angular/core';
import { ConfigService } from "../config/config.service";

@Component({
    selector: 'app-download',
    templateUrl: './download.component.html',
    styleUrls: ['./download.component.css']
})
export class DownloadComponent implements OnInit {

    constructor(
        private config: ConfigService
    ) { }

    ngOnInit() {
        this.config.setPageTitle("Download");
    }

}
