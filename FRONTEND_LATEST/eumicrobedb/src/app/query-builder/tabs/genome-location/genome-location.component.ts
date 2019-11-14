import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, FormControl, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

import { ConfigService } from "src/app/config";
import { QueryBuilderService, DataSharingService } from 'src/app/_services';

import * as DataTable from "vanilla-datatables/dist/vanilla-dataTables.min";
import Swal from 'sweetalert2';

@Component({
    selector: 'app-genome-location',
    templateUrl: './genome-location.component.html',
    styleUrls: ['./genome-location.component.css']
})
export class GenomeLocationComponent implements OnInit {

    queryForm: FormGroup;
    loading: boolean = true;
    listItems: any = [];
    queryItem: any = [];
    dataTable2: DataTable;
    currentTab: number = 2;
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
            organism_name: new FormControl("", Validators.required),
            genome_location: new FormControl("", Validators.required)
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

        this.ds.postApiData(this.config.getQueryTabUrl(this.currentTab), submitted_data)
        .then((resp:any) => {
            this.queryItem = resp.query;
            this.processingQuery = false;

            // Setting table data
            let resultItem: any = {};
            resultItem.result = [];

            resp.query.map(item => {
                if (item.length) {
                    resultItem.result.push( [
                        item[9], 
                        item[1], 
                        item[10], 
                        item[5],
                        ""
                    ] );
                }
            });

            resultItem.header = [
                "Transcript Name", 
                "Gene feature", 
                "Function/comments", 
                "Taxon Id",
                `<i class="far fa-eye hover-link toggle-table-2" title="Show Table Data"></i>`
            ];

            // Syncing data
            this.qbService.getQuery({
                query: resp.query,
                tabNo: this.currentTab + 1,
                headers: resultItem.header 
            });

            document.getElementsByTagName('form').item(this.currentTab).reset();

            window.setTimeout(function () {
                if (this.dataTable2) {
                    this.dataTable2.destroy();
                }

                this.dataTable2 = new DataTable("#genome-location-search-result", {
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
                });

                let showHideIcon = document.querySelector('.toggle-table-2');
                if (showHideIcon) {
                    showHideIcon.addEventListener('click', that.toggleDataTable.bind(that));
                }                    
            }, 100, this.dataTable2);
        })
        .catch(err => {
            this.processingQuery = false;
        });  
    }


    isAlreadyProcessed(submittedData: any) {
        let item = this.processedQueryParams.find(params => (params.organism_name === submittedData.organism_name) && (params.genome_location === submittedData.genome_location));
        return item ? true : false;
    }


    toggleDataTable(event: Event) {
        let elem = <HTMLElement>event.target;
        let tableBody = <HTMLElement>elem.closest(".dataTable-table").querySelector("tbody");
        let dataTableFooter = <HTMLElement>elem.closest(".dataTable-container").nextElementSibling;

        elem.classList.toggle("fa-eye");
        elem.classList.toggle("fa-eye-slash");

        if (elem.classList.contains("fa-eye")) {
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
