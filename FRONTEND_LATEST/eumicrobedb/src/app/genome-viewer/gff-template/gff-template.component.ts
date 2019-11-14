import { Component, OnInit } from '@angular/core';

import { ConfigService } from 'src/app/config';

@Component({
    selector: 'app-gff-template',
    templateUrl: './gff-template.component.html',
    styleUrls: ['./gff-template.component.css']
})
export class GffTemplateComponent implements OnInit {

    constructor(
        private config: ConfigService,
    ) { }

    ngOnInit() {
        this.config.setPageTitle( "Download Sequences" );
    }

}
