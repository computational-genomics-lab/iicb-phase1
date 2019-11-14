import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, FormArray, FormControl, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

import { ConfigService } from "src/app/config";
import { QueryBuilderService, DataSharingService } from 'src/app/_services';

import * as DataTable from "vanilla-datatables/dist/vanilla-dataTables.min";
import Swal from 'sweetalert2';

@Component({
    selector: 'app-protein-domain',
    templateUrl: './protein-domain.component.html',
    styleUrls: ['./protein-domain.component.css']
})
export class ProteinDomainComponent implements OnInit {

    queryForm: FormGroup;
    loading: boolean = true;
    listItems: any = [];  
    queryItem: any = [];
    organismFormArray;    
    dataTable7: DataTable;
    currentTab: number = 7;
    processingQuery: boolean = false;
    processedQueryParams: any = [];    

    constructor(
        private http: HttpClient,
        private config: ConfigService,
        private formBuilder: FormBuilder,
        private qbService: QueryBuilderService,
        private ds: DataSharingService
    ) { }


    ngOnInit() {
        this.queryForm = this.formBuilder.group({
            organism_name : new FormControl( "", Validators.required ),
            protein_domain: new FormControl( "", Validators.required )
        });

        this.qbService.listData.subscribe(items => {
            this.loading = false;
            this.listItems = items;
        });        
    }


    processQuery() {
        let that = this;
        let submitted_data = this.queryForm.value;

        if(this.isAlreadyProcessed(submitted_data)) {
            Swal.fire("", "Same query is already performed!", "warning");
            return;
        }
        
        this.processingQuery = true;
        this.processedQueryParams.push(submitted_data);          
        
        this.ds.postApiData(this.config.getQueryTabUrl( this.currentTab ), submitted_data)
        .then((resp:any) => {
            this.queryItem = resp.query;
            this.processingQuery = false;

            // Setting table data
            let resultItem: any = {};
            resultItem.result = [];

            resp.query.map(item => {
                if (item.length) {
                    resultItem.result.push( [
                        item[1], 
                        item[2], 
                        item[5],
                        ""
                    ] );
                }
            });

            resultItem.header = [
                "Transcript Name", 
                "Function/comments",                 
                "Organism",
                `<i class="far fa-eye hover-link toggle-table-7" title="Show Table Data"></i>`
            ];          
            
            // Syncing data
            this.qbService.getQuery( { 
                query: resp.query, 
                tabNo: this.currentTab + 1,
                headers: resultItem.header 
            } );

            document.getElementsByTagName('form').item( this.currentTab ).reset();

            window.setTimeout(function(){
                if( this.dataTable7 ) {
                    this.dataTable7.destroy();
                }

                this.dataTable7 = new DataTable( "#protein-domain-search-result", {
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

                let showHideIcon = document.querySelector('.toggle-table-7');
                if (showHideIcon) {
                    showHideIcon.addEventListener('click', that.toggleDataTable.bind(that));
                }                
            }, 100, this.dataTable7); 
        })
        .catch(err => {
            console.log("ERROR: ", err);
            this.processingQuery = false;
        });     
    }    


    isAlreadyProcessed(submittedData: any) {
        let item = this.processedQueryParams.find(params => (params.organism_name === submittedData.organism_name) && (params.protein_domain === submittedData.protein_domain));
        return item ? true : false;
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
