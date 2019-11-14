import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, FormControl, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { BsModalService, BsModalRef } from 'ngx-bootstrap/modal';

import { ConfigService } from "src/app/config";
import { QueryBuilderService, DataSharingService } from 'src/app/_services';

import * as DataTable from "vanilla-datatables/dist/vanilla-dataTables.min";
import Swal from 'sweetalert2';

@Component({
    selector: 'app-cluster-description',
    templateUrl: './cluster-description.component.html',
    styleUrls: ['./cluster-description.component.css']
})
export class ClusterDescriptionComponent implements OnInit {

    queryForm: FormGroup;
    queryItem: any = [];
    dataTable6: DataTable;
    currentTab: number = 6;
    bsModalRef: BsModalRef;
    processingQuery: boolean = false;
    processedQueryParams: any = [];

    constructor(
        private http: HttpClient,
        private config: ConfigService,
        private formBuilder: FormBuilder,
        private qbService: QueryBuilderService,
        private modalService: BsModalService,
        private ds: DataSharingService
    ) { }


    ngOnInit() {
        this.queryForm = this.formBuilder.group({
            cluster_description: new FormControl("", Validators.required)
        });
    }


    processQuery() {
        let that = this;
        let submitted_data = this.queryForm.value;
        this.processingQuery = true;
        this.queryItem = [];   

        this.ds.postApiData(this.config.getQueryTabUrl(this.currentTab), submitted_data)
        .then((resp:any) => {
            this.queryItem = resp.query;
            this.processingQuery = false;

            document.getElementsByTagName('form').item(this.currentTab).reset();

            // Setting table data
            let resultItem: any = {};
            resultItem.result = [];

            resp.query.map(item => {
                if (item.length) {
                    resultItem.result.push( [
                        item[7], 
                        item[6], 
                        `<img src="${ this.config.getDNDMediaUrl() + 'group' + item[6] }.dnd.png" class="modal-img hover-link" width="100" height="100">`, 
                        item[1],
                        item[4],
                        ""
                    ] );
                }
            });

            resultItem.header = [
                "Transcript Name", 
                "Cluster ID", 
                "",
                "Function/comments", 
                "Organism",
                `<i class="far fa-eye hover-link toggle-table-6" title="Show Table Data"></i>`
            ];                

            if (this.dataTable6) {
                this.dataTable6.destroy();
            }

            window.setTimeout(() => {

                this.dataTable6 = new DataTable("#cluster-description-search-result", {
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

                let el = document.querySelectorAll('.modal-img');
                if (el) {
                    el.forEach(elem => elem.addEventListener('click', this.trackImageClick.bind(this)));
                }
                
                let showHideIcon = document.querySelector('.toggle-table-6');
                if (showHideIcon) {
                    showHideIcon.addEventListener('click', that.toggleDataTable.bind(that));
                }

                this.dataTable6.on('datatable.page', (page) => {
                    let el = document.querySelectorAll('.modal-img');
                    if (el) {
                        el.forEach(elem => elem.addEventListener('click', this.trackImageClick.bind(this)));
                    }
                });
            }, 1000, this.dataTable6);
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
        this.bsModalRef = this.modalService.show(ModalContentComponent2, { initialState });
    }


    trackImageClick(event: Event) {
        let image = <HTMLImageElement>event.target;

        this.openModal(image.src);
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
export class ModalContentComponent2 implements OnInit {
    image: string;
    
    constructor(public bsModalRef: BsModalRef) { }

    ngOnInit() {

    }
}
