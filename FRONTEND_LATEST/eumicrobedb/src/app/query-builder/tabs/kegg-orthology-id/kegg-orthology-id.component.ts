import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, FormArray, FormControl, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

import { ConfigService } from "src/app/config";
import { QueryBuilderService, DataSharingService } from 'src/app/_services';

import * as DataTable from "vanilla-datatables/dist/vanilla-dataTables.min";

@Component({
    selector: 'app-kegg-orthology-id',
    templateUrl: './kegg-orthology-id.component.html',
    styleUrls: ['./kegg-orthology-id.component.css']
})
export class KeggOrthologyIdComponent implements OnInit {

    queryForm: FormGroup;
    loading: boolean = true;
    listItems: any = [];
    queryItem: any = [];  
    dataTable4: DataTable;
    currentTab: number = 4;
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
            kegg_id      : new FormControl( "", Validators.required )
        });

        this.qbService.listData.subscribe(items => {
            this.loading = false;
            this.listItems = items;
        });           
    }


    processQuery() {
        let that = this;
        let submitted_data = this.queryForm.value;
        this.processingQuery = true;  

        this.ds.postApiData(this.config.getQueryTabUrl( this.currentTab ), submitted_data)
        .then((resp:any) => {
            this.queryItem = resp.query;
            this.processingQuery = false;

            document.getElementsByTagName('form').item( this.currentTab ).reset();

            // Setting table data
            let resultItem: any = {};
            resultItem.result = [];

            resp.query.map(item => {
                if (item.length) {
                    resultItem.result.push( [
                        item[0], 
                        item[2], 
                        item[4],
                        ""
                    ] );
                }
            } );

            resultItem.header = [
                "Gene", 
                "KEGG ID", 
                "Organism",
                `<i class="far fa-eye hover-link toggle-table-4" title="Show Table Data"></i>`
            ];

            window.setTimeout(function() {
                if( this.dataTable4 ) {
                    this.dataTable4.destroy();
                }

                this.dataTable4 = new DataTable( "#kegg-orthology-search-result", {
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

                let showHideIcon = document.querySelector('.toggle-table-4');
                if (showHideIcon) {
                    showHideIcon.addEventListener('click', that.toggleDataTable.bind(that));
                }                
            }, 100, this.dataTable4);        
        })
        .catch(err => {
            console.log("ERROR: ", err);
            this.loading = this.processingQuery = false;
        });              
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

}
