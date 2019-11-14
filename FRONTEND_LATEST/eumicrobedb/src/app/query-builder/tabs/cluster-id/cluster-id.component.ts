import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, FormControl, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { BsModalService, BsModalRef } from 'ngx-bootstrap/modal';

import { ConfigService } from "src/app/config";
import { QueryBuilderService, DataSharingService } from 'src/app/_services';

import * as DataTable from "vanilla-datatables/dist/vanilla-dataTables.min";

@Component({
    selector: 'app-cluster-id',
    templateUrl: './cluster-id.component.html',
    styleUrls: ['./cluster-id.component.css']
})
export class ClusterIdComponent implements OnInit {

    queryForm: FormGroup;
    queryItem: any = [];
    dataTable5: DataTable;
    currentTab: number = 5;
    bsModalRef: BsModalRef;
    processingQuery: boolean = false;
    dndPath: string = "";

    constructor(
        private http: HttpClient,
        private config: ConfigService,
        private formBuilder: FormBuilder,
        private qbService: QueryBuilderService,
        private modalService: BsModalService,
        private ds: DataSharingService
    ) { }

    ngOnInit() {
        this.dndPath = this.config.getDNDMediaUrl();

        this.queryForm = this.formBuilder.group({
            cluster_id: new FormControl("", Validators.required)
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

    processQuery() {
        let that = this;
        let submitted_data = this.queryForm.value;
        this.processingQuery = true; 

        this.ds.postApiData(this.config.getQueryTabUrl(this.currentTab), submitted_data)
        .then((resp:any) => {
            this.queryItem = resp;
            this.processingQuery = false;

            document.getElementsByTagName('form').item(this.currentTab).reset();

            // Setting table data
            let resultItem: any = {};
            resultItem.result = [];

            resp.query.map(item => {
                if (item.length) {
                    resultItem.result.push( [
                        item[7], 
                        item[1], 
                        item[2],
                        ""
                    ] );
                }
            });

            resultItem.header = [
                "Transcript Name", 
                "Function/comments", 
                "Organism",
                `<i class="far fa-eye hover-link toggle-table-5" title="Show Table Data"></i>`
            ];

            window.setTimeout(function () {

                if (this.dataTable5) {
                    this.dataTable5.destroy();
                }                   

                this.dataTable5 = new DataTable("#cluster-id-search-result", {
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


                let showHideIcon = document.querySelector('.toggle-table-5');
                if (showHideIcon) {
                    showHideIcon.addEventListener('click', that.toggleDataTable.bind(that));
                }                    

            }, 100, this.dataTable5);
        })
        .catch(err => {
            console.log("ERROR: ", err);
            this.processingQuery = false;
        });          
    }


    openModal(imageUrl: string) {
        let initialState = {
            image: imageUrl
        };
        this.bsModalRef = this.modalService.show(ModalContentComponent1, { initialState });
    }




}
@Component({
    selector: 'modal-content',
    template: `
    <div class="modal-header">
        <h4 class="modal-title pull-left"></h4>
        <button type="button" class="close pull-right" aria-label="Close" (click)="bsModalRef.hide()">
            <span aria-hidden="true">&times;</span>
        </button>
    </div>
    <div class="modal-body">
        <img src="{{ image }}">
    </div>
    `
})
export class ModalContentComponent1 implements OnInit {
    image: string;
    
    constructor(public bsModalRef: BsModalRef) { }

    ngOnInit() {

    }
}
