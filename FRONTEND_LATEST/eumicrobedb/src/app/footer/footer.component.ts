import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

@Component({
    selector: 'app-footer',
    templateUrl: './footer.component.html',
    styleUrls: ['./footer.component.css']
})
export class FooterComponent implements OnInit {
    showFooter = true;

    constructor(private route: ActivatedRoute) { }

    ngOnInit() {
        let page_path = this.route.snapshot.url[0] ? this.route.snapshot.url[0].path : "";
        let page_url = "/" + page_path;
        this.showFooter = ! [ "/genome-viewer", "/browser-detail", "/non-coding" ].includes( page_url );        
    }

}
