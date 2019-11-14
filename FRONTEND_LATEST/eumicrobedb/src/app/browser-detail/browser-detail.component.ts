import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpClient, HttpParams } from '@angular/common/http';

import { ConfigService } from '../config/config.service';
import * as CanvasJS from '../../assets/js/canvasjs.min';
import Swal from 'sweetalert2';
import { DomSanitizer } from '@angular/platform-browser';
import { DataSharingService } from '../_services';

@Component({
    selector: 'app-browser-detail',
    templateUrl: './browser-detail.component.html',
    styleUrls: ['./browser-detail.component.css']
})
export class BrowserDetailComponent implements OnInit {

    loading :boolean = true;
    tabLoading :boolean = false;
    urlParams: any;
    data: any;
    sequence: string = "";
    tabData: any;
    tabContent: any;
    uiTabs: any[] = [];

    pageNavigations = [
        'Analysis',
        'FPRINTSCAN',
        'ProfileScan',
        'HmmSmart',
        'InterPro',
        'GO',
    ];

    analysisTabs = [
        "PLOTORF",
        "prettyseq",
        "remap",
        "showpep",
        "sixpack",
        "revseq",
        "banana",
        "btwisted",
        "sirna",
        "cai",
        "cusp",
        "cpgplot",
        "geecee",
        "eprimer32",
        "tfscan",
        "CLEAR ALL"
    ];

    // Scaffold options
    sc_rects = [];
    sc_lines = [];
    sc_plus_width: number = 50;
    sc_width_const: number = 1;
    sc_svg_width: number = 778;
    motif_svg_width = 450;
    supportedImages = [ "png", "jpg", "gif" ];
    static_file_path: string = this.config.getBrowserDetailsMediaUrl();

    constructor(
        private config: ConfigService,
        private http: HttpClient,
        private route: ActivatedRoute,
        private router: Router,
        private sanitizer: DomSanitizer,
        private ds: DataSharingService
    ) { }

    ngOnInit() {
        this.config.setPageTitle("Browser Detail");

        this.route
        .queryParams
        .subscribe(params => {
            this.urlParams = params;

            // Make a post request
            this.ds.postApiData(this.config.getBrowserDetailUrl(), this.urlParams)
            .then((resp:any) => {
                this.loading = false;
                this.data = resp;

                if (this.data.NCBIlink.includes('?')) {
                    const httpParams = new HttpParams({ fromString: this.data.NCBIlink.split('?')[1] });
                    this.sequence = httpParams.get('QUERY');
                }


                // Fickett Chart Data Setup
                let fickettChartData = this.data.Flickett_res;
                let fickett_line1_data = [];
                let fickett_line2_data = [];

                fickettChartData.forEach((row: any) => {
                    fickett_line1_data.push({
                        x: Number( row[0] ),
                        y: Number( row[1] )
                    });

                    fickett_line2_data.push({
                        x: Number( row[0] ),
                        y: Number( row[2] )
                    });
                });


                // Loglikelihood Chart Data Setup
                let logChartData = this.data.LogLkhd_res;
                let log_line1_data = [];
                let log_line2_data = [];
                let log_line3_data = [];
                let log_line4_data = [];
                let log_line5_data = [];
                let log_line6_data = [];

                logChartData.forEach((row: any) => {
                    log_line1_data.push({
                        x: Number( row[0] ),
                        y: Number( row[1] )
                    });

                    log_line2_data.push({
                        x: Number( row[0] ),
                        y: Number( row[2] )
                    });

                    log_line3_data.push({
                        x: Number( row[0] ),
                        y: Number( row[3] )
                    });

                    log_line4_data.push({
                        x: Number( row[0] ),
                        y: Number( row[4] )
                    });

                    log_line5_data.push({
                        x: Number( row[0] ),
                        y: Number( row[5] )
                    });

                    log_line6_data.push({
                        x: Number( row[0] ),
                        y: Number( row[6] )
                    });
                });

                setTimeout(() => {
                    // Scaffold Position
                    let rects = [];
                    this.sc_width_const = this.data.scaffold_pos.rect.reverse()[0].rect_r / this.sc_svg_width;

                    this.data.scaffold_pos.rect.forEach(rect => {
                        let rect_width = ( parseInt( rect.rect_r ) - parseInt( rect.rect_l ) ) / this.sc_width_const;

                        rects.push({
                            position_x        : this.sc_plus_width + ( parseInt( rect.rect_l ) / this.sc_width_const ),
                            position_y        : this.sc_plus_width + ( parseInt( rect.rect_r ) / this.sc_width_const ),
                            left_top_label    : parseInt( rect.vert_l_top_label ),
                            left_bottom_label : parseInt( rect.vert_l_bot_label ),
                            right_top_label   : parseInt( rect.vert_r_top_label ),
                            right_bottom_label: parseInt( rect.vert_r_bot_label ),
                            right_line_start  : rect_width + this.sc_plus_width + ( parseInt( rect.rect_l ) / this.sc_width_const ),
                            width             : rect_width
                        });
                    });

                    this.sc_rects = rects;
                    this.sc_lines = this.data.scaffold_pos.lines;

                    // Fickett Chart
                    var fickett_chart = new CanvasJS.Chart("fickettChartContainer", {
                        animationEnabled: true,
                        zoomEnabled: true,
                        title: {
                            text: "Ficket Plot for the sequence",
                            fontSize: 25,
                            fontColor: "#0000ff"
                        },
                        axisX:{
                            title: "base position",
                            titleFontSize: 12,
                            crosshair: {
                                enabled: true,
                                snapToDataPoint: true
                            },
                            maximum: null
                        },
                        axisY: {
                            title: "fickett score",
                            interval: 0.4,
                            maximum: 2,
                            gridThickness: 0,
                            stripLines: [{
                                value: 0.75
                            }]
                        },
                        toolTip: {
                            shared: true
                        },
                        legend: {
                            cursor: "pointer"
                        },
                        data: [{
                            type: "line",
                            name: "+ strand",
                            color: "#ff0000",
                            showInLegend: true,
                            markerSize: 0,
                            lineThickness: 1,
                            dataPoints: fickett_line1_data
                        },
                        {
                            type: "line",
                            name: "- strand",
                            color: "#0f0",
                            showInLegend: true,
                            markerSize: 0,
                            lineThickness: 1,
                            dataPoints: fickett_line2_data
                        }]
                    });

                    fickett_chart.render();

                    // Loglikelihood Chart
                    var log_chart = new CanvasJS.Chart("logChartContainer", {
                        animationEnabled: true,
                        zoomEnabled: true,
                        creditText: "",
                        title: {
                            text: "Loglikelihood Plot for the sequence",
                            fontSize: 25,
                            fontColor: "#0000ff"
                        },
                        axisX:{
                            title: "base position",
                            titleFontSize: 12,
                            crosshair: {
                                enabled: true,
                                snapToDataPoint: true
                            },
                            maximum: null
                        },
                        axisY: {
                            title: "loglikelihood score",
                            interval: 8,
                            maximum: 25,
                            gridThickness: 0,
                            stripLines: [{
                                value: 0.95
                            }],
                            includeZero: false,
                            minimum: -15,
                            viewportMinimum: -15,
                        },
                        toolTip: {
                            shared: true
                        },
                        legend: {
                            cursor: "pointer"
                        },
                        data: [{
                            type: "line",
                            name: "+1",
                            color: "#f00",
                            showInLegend: true,
                            markerSize: 0,
                            lineThickness: 1,
                            dataPoints: log_line1_data
                        },
                        {
                            type: "line",
                            name: "+2",
                            color: "#0f0",
                            showInLegend: true,
                            markerSize: 0,
                            lineThickness: 1,
                            dataPoints: log_line2_data
                        },
                        {
                            type: "line",
                            name: "+3",
                            color: "#00f",
                            showInLegend: true,
                            markerSize: 0,
                            lineThickness: 1,
                            dataPoints: log_line3_data
                        },
                        {
                            type: "line",
                            name: "-1",
                            color: "#ff0",
                            showInLegend: true,
                            markerSize: 0,
                            lineThickness: 1,
                            dataPoints: log_line4_data
                        },
                        {
                            type: "line",
                            name: "-2",
                            color: "#f0f",
                            showInLegend: true,
                            markerSize: 0,
                            lineThickness: 1,
                            dataPoints: log_line5_data
                        },
                        {
                            type: "line",
                            name: "-3",
                            color: "#0ff",
                            showInLegend: true,
                            markerSize: 0,
                            lineThickness: 1,
                            dataPoints: log_line6_data
                        }]
                    });

                    log_chart.render();
                }, 100);
            })
            .catch(err => this.loading = false); 
        } );
    }


    moveTo( elem: any ) {
        let position = elem.target.dataset.to;
        document.getElementById('block-' + position)
        .scrollIntoView( {
            behavior: "smooth",
            block   : "start",
            inline  : "nearest"
        } );
    }


    getSantizeUrl(url : string) {
        return this.sanitizer.bypassSecurityTrustHtml(url);
    }


    fetchTabData( tabName: string ) {
        let clearTabBtn = document.getElementById("tab-CLEARALL");
        let functionName = tabName.toLowerCase();

        if( tabName === "CLEAR ALL" ) {
            this.uiTabs = [];
            document.querySelectorAll(".btn-tab").forEach(btn => btn.removeAttribute("disabled"));
            clearTabBtn.setAttribute("disabled", "disabled");
            return;
        }

        this.tabLoading = true;

        let postData = {
            function: functionName,
            ID: 68,
            sequence: this.sequence
        };

        this.ds.postApiData(this.config.getBrowserDetailTabUrl(), postData)
        .then(async (resp:any) => {
            const promises = [];
            let imageCount = 0;
            let data = `<h2>${ functionName }</h2><br>`;
            let fileNames: [] = resp.filename.split(",");
            let fileExt: [] = resp.type.split(",");
            this.tabLoading = false;

            switch ( resp.status ) {
                case 0: Swal.fire('', 'Something went wrong. Please try again later.', 'info');
                        return;
                        break;

                case 1: // handle text file
                    // await this.getTextMarkup( functionName, resp.filename ).then( text => data += '<div><pre>' + text + '</pre></div>' );
                    
                    fileNames.forEach( (ext, index) => {
                        promises.push( this.ds.getApiData( this.static_file_path + functionName + "/" + fileNames[ index ], "" ).then( text => text ) );
                    });        
                    
                    const [...textDatas] = await Promise.all(promises);

                    fileNames.forEach( (ext, index) => {
                        data += '<div class="mb-3"><pre>' + textDatas[index] + '</pre></div>';
                    });                    
                    break;

                case 2: // handle image file
                    // data += this.getImageMarkup( functionName, resp.filename, resp.type );
                    
                    fileExt.forEach( (ext, index) => {
                        if( this.supportedImages.includes( ext )  ) {
                            promises.push( this.static_file_path + functionName + "/" + fileNames[ index ] + "." + ext );
                        }
                    });

                    const [...imageDatas] = await Promise.all(promises);

                    fileExt.forEach( (ext, index) => {
                        if( this.supportedImages.includes( ext )  ) {
                            imageCount += 1;
                            data += `<h5 class="text-dark">${ functionName + imageCount } image</h5><img src="${ imageDatas[index] }" class="mb-3">`;
                        }
                    });                    
                    break;

                case 3: // handle text + image

                    fileExt.forEach( (ext, index) => {
                        if( ['txt', 'none'].includes(ext) ) {
                            // promises.push( fetch( this.static_file_path + functionName + "/" + fileNames[ index ] ).then( res => res.text() ).then( text => text ) );
                            promises.push( this.ds.getApiData( this.static_file_path + functionName + "/" + fileNames[ index ], "" ).then( text => text ) );
                        } else if( this.supportedImages.includes( ext )  ) {
                            promises.push( this.static_file_path + functionName + "/" + fileNames[ index ] + "." + ext );
                        }
                    });

                    const [...datas] = await Promise.all(promises);

                    fileExt.forEach( (ext, index) => {
                        if( ['txt', 'none'].includes(ext) ) {
                            data += '<div class="mb-3"><pre>' + datas[index] + '</pre></div>';
                        } else if( this.supportedImages.includes( ext )  ) {
                            imageCount += 1;
                            data += `<h5 class="text-dark">${ functionName + imageCount } image</h5><img src="${ datas[index] }" class="mb-3">`;
                        }
                    });

                    break;
            }

            clearTabBtn.removeAttribute('disabled');
            this.addNewTab( functionName, data );
            document.getElementById( 'tab-' + tabName ).setAttribute('disabled', 'disabled');
        })
        .catch(err => this.tabLoading = false); 

    }


    addNewTab( tabTitle: string, tabContent: string ): void {
        this.uiTabs.map( tab => tab.active = false );

        this.uiTabs.push({
            title      : tabTitle,
            content    : tabContent,
            active     : true,
            disabled   : false,
            removable  : false
        });
    }


    viewList( item: object ) {
        this.router.navigate( ['/genome-viewer'], { queryParams: item } );
    }


    getImageMarkup( storagepath: string, filename: string, filetype: string ) {
        return `<img src="${ this.static_file_path + storagepath + "/" + filename + "." + filetype }">`;
    }


    getTextMarkup( storagepath: string, filename: string ) {
        const fileUrl = this.static_file_path + storagepath + "/" + filename;

        return new Promise( (resolve, reject) => {
            var myRequest = new Request(fileUrl);
            fetch(myRequest)
            .then(function(response) {
                return response.text().then(function(text) {
                    resolve( text );
                });
            });
        } );
    }


    openScaffoldLinkDetails() {
        this.router.navigate( ['/scaffold-details'], { queryParams: this.data.scaffold_pos_link } );
    }
}
