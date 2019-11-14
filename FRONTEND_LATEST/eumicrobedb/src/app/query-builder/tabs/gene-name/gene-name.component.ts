import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, FormControl, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

import { ConfigService } from "src/app/config";
import { QueryBuilderService, DataSharingService } from 'src/app/_services';

import * as DataTable from "vanilla-datatables/dist/vanilla-dataTables.min";

@Component({
    selector: 'app-gene-name',
    templateUrl: './gene-name.component.html',
    styleUrls: ['./gene-name.component.css']
})
export class GeneNameComponent implements OnInit {

    queryForm: FormGroup;
    loading: boolean = true;
    listItems: any = [];
    queryItem: any = [];
    dataTable0: DataTable;
    currentTab: number = 0;
    resultCount: number = 0;    
    processingQuery: boolean = false;

    constructor(
        private http: HttpClient,
        private config: ConfigService,
        private formBuilder: FormBuilder,
        private qbService: QueryBuilderService,
        private ds: DataSharingService
    ) { }


    ngOnInit() {
        this.queryForm = this.formBuilder.group({
            organism_name: new FormControl( "", Validators.required ),
            gene_name    : new FormControl( "", Validators.required )
        });

        this.qbService.listData.subscribe(items => {
            this.loading   = false;
            this.listItems = items;
        });
    }


    toggleTable(event: Event) {
        let elem = <HTMLElement> event.target;
        let tableBody = <HTMLElement> document.querySelector(".sample-table-body");

        elem.classList.toggle( "fa-eye" );
        elem.classList.toggle( "fa-eye-slash" );

        if( elem.classList.contains("fa-eye") ) {
            tableBody.style.display = "table-row-group";
            elem.setAttribute("title", "Hide Table Data");
        } else {
            tableBody.style.display = "none";
            elem.setAttribute("title", "Show Table Data");
        }        
    }


    toggleDataTable(event: Event) {
        let elem = <HTMLElement> event.target;
        let tableBody = <HTMLElement> elem.closest(".dataTable-table").querySelector("tbody");
        let dataTableFooter = <HTMLElement> elem.closest(".dataTable-container").nextElementSibling;

        elem.classList.toggle( "fa-eye" );
        elem.classList.toggle( "fa-eye-slash" );

        if( elem.classList.contains("fa-eye") ) {
            tableBody.style.display = "table-row-group";
            elem.setAttribute("title", "Hide Table Data");
            dataTableFooter.style.display = "block";
        } else {
            tableBody.style.display = "none";
            elem.setAttribute("title", "Show Table Data");
            dataTableFooter.style.display = "none";
        }        
    }     


    processQuery() {
        let that = this;
        let submitted_data = this.queryForm.value;
        this.processingQuery = true;        
        
        this.ds.postApiData(this.config.getQueryTabUrl( this.currentTab ), submitted_data)
        .then((resp:any) => {
            this.resultCount = 0;            
            this.queryItem = resp.query;
            this.processingQuery = false;

            document.getElementsByTagName('form').item( this.currentTab ).reset();

            if(! this.queryItem.length) {
                return false;
            }

            console.log("processed...");

            // Setting table data
            let resultItem: any = {};
            resultItem.result = [];
            this.queryItem.map(item => {
                if (item.length) {
                    resultItem.result.push( [ 
                        item[1], 
                        item[2], 
                        item[6],
                        ""
                    ] );
                    this.resultCount++;
                }
            });    
            resultItem.header = [
                "Transcript Name", 
                "Function/comments", 
                "Taxon ID",
                `<i class="far fa-eye hover-link toggle-table-0" title="Show Table Data"></i>`
            ];        

            window.setTimeout(function(){        
                if( that.dataTable0 ) {
                    that.dataTable0.destroy();
                }

                this.dataTable0 = new DataTable( "#gene-name-search-result", {
                    perPageSelect: false,
                    perPage: 12,
                    searchable: false,
                    sortable: false,
                    data: {
                        "headings": resultItem.header,
                        "data": resultItem.result
                    },                    
                    labels: {
                        noRows: "No result found",
                        info: "Page {page} of {pages}",
                    }
                } );

                let showHideIcon = document.querySelector('.toggle-table-0');
                if (showHideIcon) {
                    showHideIcon.addEventListener('click', that.toggleDataTable.bind(that));
                }                
            }, 100, this.dataTable0);
        })
        .catch(err => {
            console.log("ERROR: ", err);
            this.processingQuery = false;
        });          
    }    

}
