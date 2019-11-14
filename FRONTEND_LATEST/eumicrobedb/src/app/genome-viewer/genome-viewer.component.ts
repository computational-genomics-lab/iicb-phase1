import { Component, OnInit, OnDestroy, TemplateRef } from '@angular/core';

import { HttpClient } from '@angular/common/http';
import { ActivatedRoute } from '@angular/router';
import { Subscription }   from 'rxjs';
import { saveAs } from 'file-saver';
import { BsModalService, BsModalRef } from 'ngx-bootstrap/modal';

import { ConfigService } from "../config";
import { Tracks } from "../_models";
import { GnomeToolbox } from '../_services';
import { DataSharingService } from 'src/app/_services';
import { error } from 'util';

import * as PouchDB from 'src/assets/js/pouchdb.min';
import Swal from 'sweetalert2';

declare var genomeTrack: any;
declare var linearBrush: any;

@Component({
    selector: 'app-genome-viewer',
    templateUrl: './genome-viewer.component.html',
    styleUrls: ['./genome-viewer.component.css']
})
export class GenomeViewerComponent implements OnInit {

    loading: boolean = true;
    linearTrack: any;
    brush: any;
    trackChildren: Element;
    trackData: any;
    trackStart = 0;
    trackEnd = 150000;
    moveIndex = 150000;
    trackLabelInitialized: boolean = false;

    /* Initialize the layout for the linear plot, the base
   parameters such as the genome size, the height of the
   plot in px, the width of the plot, the div container to
   put the SVG element, and an initial zoom level */
    linearlayout = {
        genomesize: 450000,
        height: 1800,
        width: 900,
        container: "#linearchart",
        initStart: this.trackStart,
        initEnd: this.trackEnd,
    };

    /* Initialize the layout for the linear brush, including
       what container to put the brush in to */
    contextLayout = {
        genomesize: 1050000,
        container: "#brush"
    };

    urlParams: any;
    genome_label: string;
    downloadScaffoldData: string;

    moveLeftSubscription: Subscription;
    moveRightSubscription: Subscription;
    prevScaffoldSubscription: Subscription;
    nextScaffoldSubscription: Subscription;

    modalRef: BsModalRef;

    gffFile: any;

    iicbDB: any;

    constructor(
        private http: HttpClient, 
        private route: ActivatedRoute, 
        private config: ConfigService,
        private genomeTool: GnomeToolbox,
        private ds: DataSharingService,
        private modalService: BsModalService,
    ) {        
        this.iicbDB = new PouchDB('iicb', {auto_compaction: true});
    }

    ngOnInit() {
        this.config.setPageTitle( "Genome Viewer" );


        this.moveLeftSubscription = this.genomeTool.btnMoveLeftAction$.subscribe(_ => {
            this.moveLeft();
        } );
        
        this.moveRightSubscription = this.genomeTool.btnMoveRightAction$.subscribe(_ => {
            this.moveRight();
        } );

        this.prevScaffoldSubscription = this.genomeTool.btnScaffoldLeftAction$.subscribe(_ => {
            this.movePrevScaffold();
        });

        this.nextScaffoldSubscription = this.genomeTool.btnScaffoldRightAction$.subscribe(_ => {
            this.moveNextScaffold();
        });


        // Parse url params
        this.route
        .queryParams
        .subscribe(params => { 
            this.urlParams = params;
            this.genome_label = params.label;

            this.ds.postApiData(this.config.getapiGenomeUrl(), this.urlParams)
            .then((resp:any) => {
                this.loading = false;
                this.trackData = resp.tracks;
                this.downloadScaffoldData = resp.scaffold_dnld;
                
                this.displayTrack( this.linearlayout, this.trackData );
                let adb = this.iicbDB;

                // Insert dummy blank track at the beginning
                let parsedTracks = this.trackData;
                parsedTracks.unshift({ 
                    "trackName": "",
                    "trackType": "track",
                    "visible": true,
                    "inner_radius": 80,
                    "outer_radius": 120,
                    "trackFeatures": "complex",
                    "featureThreshold": 7000000,
                    "mouseover_callback": "islandPopup",
                    "mouseout_callback": "islandPopupClear",
                    "linear_mouseclick": [
                        "linearPopup",
                        "linearClick"
                    ],
                    "showLabels": true,
                    "showTooltip": true,
                    "items": []
                });

                // save to indexed db
                this.iicbDB.get('chromosome').then(function (doc) {             
    
                    return adb.put({
                        _id: 'chromosome',
                        _rev: doc._rev,
                        cdata: parsedTracks
                    });
                }).then(function (response) {
                    // handle response
                }).catch(function (err) {
    
                    adb.put({
                        _id: 'chromosome',
                        cdata: parsedTracks
                    }).then(function (response) {
                        // handle response
                    }).catch(function (err) {
                        console.log(err);
                    });                
                });                
            })
            .catch(err => this.loading = false);                   
        });
    }

    ngOnDestroy() {
        // prevent memory leak when component destroyed
        this.moveLeftSubscription.unsubscribe();
        this.moveRightSubscription.unsubscribe();
        this.prevScaffoldSubscription.unsubscribe();
        this.nextScaffoldSubscription.unsubscribe();
    }


    displayTrack( layout, tracks ) {
        this.linearTrack = new genomeTrack(layout, tracks);        
        this.brush = new linearBrush(this.contextLayout, this.linearTrack);        
        this.linearTrack.addBrushCallback(this.brush);                    
    }


    moveLeft() {
        if( this.linearlayout.initStart === 0 && this.linearTrack.visStart === 0 ) {
            return;
        }

        this.linearlayout.initStart = this.linearTrack.initStart < 1 ? 0 : ( this.linearlayout.initStart - this.moveIndex );
        this.linearlayout.initEnd = this.linearTrack.initStart < this.moveIndex ? this.moveIndex : ( this.linearlayout.initEnd - this.moveIndex );   
        this.linearTrack.update( this.linearlayout.initStart, this.linearlayout.initEnd );
        this.linearTrack.addBrushCallback(this.brush);
        
        let position_label1 = <HTMLElement> document.querySelector(".genome-position");
        position_label1.innerText = `Scaffold_1:${ this.linearlayout.initStart }-${ this.linearlayout.initEnd }`;
        let position_label2 = <HTMLElement> document.querySelector(".genome-location-label");
        position_label2.innerText = `${ this.linearlayout.initStart }-${ this.linearlayout.initEnd }`;
    }


    moveRight() {    
        let moveEnd = this.linearlayout.initEnd + this.moveIndex;
        if( moveEnd > this.contextLayout.genomesize ) {
            return;
        }

        this.linearlayout.initStart = this.linearlayout.initStart + this.moveIndex;
        this.linearlayout.initEnd = moveEnd;

        this.linearTrack.update( this.linearlayout.initStart, this.linearlayout.initEnd );
        this.linearTrack.addBrushCallback(this.brush);

        let position_label1 = <HTMLElement> document.querySelector(".genome-position");
        position_label1.innerText = `Scaffold_1:${ this.linearlayout.initStart }-${ this.linearlayout.initEnd }`;
        let position_label2 = <HTMLElement> document.querySelector(".genome-location-label");
        position_label2.innerText = `${ this.linearlayout.initStart }-${ this.linearlayout.initEnd }`;
    }
    

    toggleTrack( trackName: string, action: string ) {
        let elem = <HTMLElement> document.querySelector(`[class="${ trackName }"]`);
        elem.style.display = action;
    }


    saveScaffoldDatatoFile() {
        var blob = new Blob([this.downloadScaffoldData], { type: "text/plain;charset=utf-8" });
        saveAs(blob, "scaffold.txt");
    }


    movePrevScaffold() {        
        let scaffoldParamIndex = parseInt( this.urlParams.scaffold.split("_")[1] );

        if( scaffoldParamIndex === 1 ) {
            return;
        }

        let searchParams = new URLSearchParams({
            label    : this.urlParams.label,
            organism : this.urlParams.organism,
            scaffold : `Scaffold_${ scaffoldParamIndex - 1 }`,
            star     : this.urlParams.star,
            startbase: this.urlParams.startbase,
            stopbase : this.urlParams.stopbase,
            version  : this.urlParams.version
        });
        window.location.href = window.location.origin + "/genome-viewer?" + searchParams;  
    }


    moveNextScaffold() { 
        let scaffoldParamIndex = parseInt( this.urlParams.scaffold.split("_")[1] );        
        let searchParams = new URLSearchParams({
            label    : this.urlParams.label,
            organism : this.urlParams.organism,
            scaffold : `Scaffold_${ scaffoldParamIndex + 1 }`,
            star     : this.urlParams.star,
            startbase: this.urlParams.startbase,
            stopbase : this.urlParams.stopbase,
            version  : this.urlParams.version
        });
        window.location.href = window.location.origin + "/genome-viewer?" + searchParams;        
    }


    openModal(template: TemplateRef<any>) {
        this.modalRef = this.modalService.show(template);
    }
    
    setgffFile(e: any) {
        this.gffFile = e.target.files;
    }


    uploadGFF() {
        let formData: FormData = new FormData();
        let uploadedFile = this.gffFile.item(0);
        
        if ("gff" !== uploadedFile.name.split(".").reverse()[0]) {
            Swal.fire("", "Uploaded file type is not supported", "error");
            return;
        }
        
        if (uploadedFile.size / (1024 * 1024) > 10) {
            Swal.fire("", "Uploaded file size is should be less than 10mb", "error");
            return;
        }

        this.loading = true;

        formData.append("file", uploadedFile);
        formData.append("param", JSON.stringify(this.urlParams));
               
        this.ds.formApiData(this.config.getGffUploadUrl(), formData)
        .then((resp:any) => {
            let savedTracks = [];
            let that = this;

            this.iicbDB.get('chromosome').then(function (doc) {
                savedTracks = doc.cdata;

                Object.keys(resp.upload_tracks).forEach(function(trackName) {
                    savedTracks.unshift({ 
                        "trackName": trackName,
                        "trackType": "track",
                        "visible": true,
                        "inner_radius": 80,
                        "outer_radius": 120,
                        "trackFeatures": "complex",
                        "featureThreshold": 7000000,
                        "mouseover_callback": "islandPopup",
                        "mouseout_callback": "islandPopupClear",
                        "linear_mouseclick": [
                            "linearPopup",
                            "linearClick"
                        ],
                        "showLabels": true,
                        "showTooltip": true,
                        "items": resp.upload_tracks[trackName]
                    });
                });             
    
                that.loading = false;
                that.trackData = savedTracks;
                that.downloadScaffoldData = resp.scaffold_dnld;
                
                that.displayTrack( that.linearlayout, that.trackData );              
            }).then(function (response) {
                // handle response
            }).catch(function (err) {
                console.log(err);                 
            });
        })
        .catch(err => this.loading = false);  
    }

}


