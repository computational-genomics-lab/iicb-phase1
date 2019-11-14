import { Component, OnInit, ElementRef } from '@angular/core';
import { FormBuilder, FormGroup, FormControl, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

import { ConfigService } from "src/app/config";
import { QueryBuilderService, DataSharingService } from 'src/app/_services';

import * as DataTable from "vanilla-datatables/dist/vanilla-dataTables.min";
import Swal from 'sweetalert2';

@Component({
    selector: 'app-conserved-regions',
    templateUrl: './conserved-regions.component.html',
    styleUrls: ['./conserved-regions.component.css']
})
export class ConservedRegionsComponent implements OnInit {

    queryForm: FormGroup;
    loading: boolean = true;
    listItems: any = [];
    queryItem: any;
    dataTable3: DataTable;
    currentTab: number = 3;
    processingQuery: boolean = false;
    processedQueryParams: any = [];

    constructor(
        private http: HttpClient,
        private config: ConfigService,
        private formBuilder: FormBuilder,
        private qbService: QueryBuilderService,
        private elementRef: ElementRef,
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
        
        this.processingQuery = true;
        this.processedQueryParams.push(submitted_data);   

        this.ds.postApiData(this.config.getQueryTabUrl(this.currentTab), submitted_data)
        .then((resp:any) => {
            this.queryItem = resp;
            this.processingQuery = false;

            let filteredQuery = resp.query.map(item => [
                item[10],
                item[8] + ":" + item[2] + "-" + item[3],
                this.queryItem.target_organism,
                this.queryItem.source_id + ":" + item[0] + "-" + item[1]
            ]);

            document.getElementsByTagName('form').item(this.currentTab).reset();

            // Setting table data
            let resultItem: any = {};
            resultItem.result = [];

            resp.query.map(item => {
                if (item.length) {
                    resultItem.result.push([
                        item[10],
                        item[8] + ":" + item[2] + "-" + item[3],
                        this.queryItem.target_organism,
                        this.queryItem.source_id + ":" + item[0] + "-" + item[1],
                        ""
                    ]);
                }
            });

            resultItem.header = [
                "Target Organism",
                "Target Scaffold:Location",
                "Query organism",
                "Query Scaffold:Location",
                `<i class="far fa-eye hover-link toggle-table-3" title="Show Table Data"></i>`
            ];

            if (this.dataTable3) {
                this.dataTable3.destroy();
            }

            window.setTimeout(function () {
                this.dataTable3 = new DataTable("#conserved-regions-search-result", {
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

                let showHideIcon = document.querySelector('.toggle-table-3');
                if (showHideIcon) {
                    showHideIcon.addEventListener('click', that.toggleDataTable.bind(that));
                }
            }, 100, this.dataTable3);
        })
        .catch(err => { 
            this.loading = this.processingQuery = false;
        }); 
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
