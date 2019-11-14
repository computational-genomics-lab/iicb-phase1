import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

@Component({
    selector: 'app-nav-bar',
    templateUrl: './nav-bar.component.html',
    styleUrls: ['./nav-bar.component.css']
})
export class NavBarComponent implements OnInit {
    fullNav = false;

    constructor(private route: ActivatedRoute) {}

    ngOnInit() {
        let page_path = this.route.snapshot.url[0] ? this.route.snapshot.url[0].path : "";
        let page_url = "/" + page_path;
        this.fullNav = [ "/genome-viewer", "/browser-detail", "/non-coding", "/scaffold-details" ].includes( page_url );
    }

}
