import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, FormControl, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

import { ConfigService } from "src/app/config";
import { QueryBuilderService, DataSharingService } from 'src/app/_services';

import * as DataTable from "vanilla-datatables/dist/vanilla-dataTables.min";
import Swal from 'sweetalert2';

declare var Choices: any;
@Component({
    selector: 'app-query-builder-form',
    templateUrl: './query-builder-form.component.html',
    styleUrls: ['./query-builder-form.component.css']
})
export class QueryBuilderFormComponent implements OnInit {

    loading: boolean = false;
    joinQueryForm: FormGroup;

    // Storing pill boxes (blue & green)
    pillItems: any[] = [];

    // Storing tab nos.
    tabItems: any[] = [];

    // Search & display query result in template as table
    jointQueryResult: any;

    // Select box dropdown options
    queryItems: any[] = [];

    // Storing all search results (performed between individual tabs / query results )
    searchItems: any[] = [];

    // Storing all search headers (performed between individual tabs / query results )
    tableHeaders: any[] = [];

    // Storing query results table headers
    searchHeaders: any[] = [];

    // Datatable
    dataTable99: DataTable;
    seachdataTable: DataTable;

    // Table Wrappers
    table1Wrapper: HTMLDivElement;
    table2Wrapper: HTMLDivElement;

    // jointQueryResult
    jointQueryResultTotal: number;

    // Tab display
    tabNames = [
        "Gene Name",
        "Primary Annotation",
        "Genome Location",
        "Conserved Regions",
        "KEGG Orthology Id",
        "Cluster Id",
        "Cluster Description",
        "Protein Domain/Motif/Function",
        "SECRETOME/PROP/PSORT/SignalP/TMHMM"
    ];

    // Operator selectbox icons
    optIcons = {
        'difference'  : 'icon-difference',
        'intersection': 'icon-intersection',
        'union'       : 'icon-union'
    };

    // Saving total join query count between two tabs
    jointCount: number = 0;

    // Store joint query form search params
    processedQueryParams: any = [];

    constructor(
        private http: HttpClient,
        private config: ConfigService,
        private formBuilder: FormBuilder,
        private qbService: QueryBuilderService,
        private ds: DataSharingService
    ) { }


    ngOnInit() {
        var optIcons = this.optIcons;

        new Choices(document.getElementById('operator'), {
            itemSelectText: '',
            searchEnabled: false,
            callbackOnCreateTemplates: function (strToEl) {
                var classNames = this.config.classNames;
                var itemSelectText = this.config.itemSelectText;
                return {
                    item: function (classNames, data) {
                        return strToEl('\
                            <div\
                            class="'+ String(classNames.item) + ' ' + String(data.highlighted ? classNames.highlightedState : classNames.itemSelectable) + '"\
                            data-item\
                            data-id="'+ String(data.id) + '"\
                            data-value="'+ String(data.value) + '"\
                            '+ String(data.active ? 'aria-selected="true"' : '') + '\
                            '+ String(data.disabled ? 'aria-disabled="true"' : '') + '\
                            >\
                            <span style="margin-right:10px;"><i class="'+ optIcons[data.value] + '"></i></span> ' + String(data.label) + '\
                            </div>\
                        ');
                    },
                    choice: function (classNames, data) {
                        return strToEl('\
                            <div\
                            class="'+ String(classNames.item) + ' ' + String(classNames.itemChoice) + ' ' + String(data.disabled ? classNames.itemDisabled : classNames.itemSelectable) + '"\
                            data-select-text="'+ String(itemSelectText) + '"\
                            data-choice \
                            '+ String(data.disabled ? 'data-choice-disabled aria-disabled="true"' : 'data-choice-selectable') + '\
                            data-id="'+ String(data.id) + '"\
                            data-value="'+ String(data.value) + '"\
                            '+ String(data.groupId > 0 ? 'role="treeitem"' : 'role="option"') + '\
                            >\
                            <span style="margin-right:10px;"><i class="'+ optIcons[data.value] + '"></i></span> ' + String(data.label) + '\
                            </div>\
                        ');
                    },
                };
            }
        });

        this.table1Wrapper = <HTMLDivElement> document.getElementById("query-builder-search-result-wrap");
        this.table2Wrapper = <HTMLDivElement> document.getElementById("output-search-result-wrap");

        // Recieving & manipulating results from individual tabs
        this.qbService.queryData.subscribe((data: any) => {

            // if (!this.tabItems.includes(data.tabNo)) {
                this.tabItems.push(data.tabNo);
                this.searchItems.push(data.query);
                this.tableHeaders.push(data.headers);

                this.queryItems.push({
                    text: this.tabNames[data.tabNo - 1] + ` (${data.query.length})`
                });

                this.pillItems.push({
                    type: "primary",
                    text: this.tabNames[data.tabNo - 1] + ` (${data.query.length})`,
                    tabNo: data.tabNo
                });
            // }

            console.log( this.tabItems, this.searchItems );
        });

        this.joinQueryForm = this.formBuilder.group({
            query_1: new FormControl("", Validators.required),
            query_2: new FormControl("", Validators.required),
            operator: new FormControl("", Validators.required)
        });
    }


    switchTabCommand( resultIndex: number, event: Event ) {
        // this.qbService.switchTab( tabNo );

        let item = <HTMLSpanElement> event.target;

        if (this.seachdataTable) {
            this.seachdataTable.destroy();
        }

        let resultItem = this.searchItems[resultIndex];
        let resultHeader = this.tableHeaders[resultIndex];
        let tabNo = this.tabItems[resultIndex];

        window.setTimeout(() => {

            if( this.table1Wrapper ) {
                this.table1Wrapper.classList.add("d-none");
            }
            this.table2Wrapper.classList.remove("d-none");
            if( tabNo < 10 ) {
                resultHeader[resultHeader.length -1] = "";
                this.table2Wrapper.classList.add("hide-last");
            } else {
                // resultHeader[resultHeader.length] = "";
                this.table2Wrapper.classList.remove("hide-last");
            }

            document.querySelector(".output-heading").innerHTML = item.innerHTML;

            this.seachdataTable = new DataTable("#output-search-result", {
                perPageSelect: false,
                perPage: 12,
                searchable: false,
                sortable: false,
                data: {
                    "headings": resultHeader,
                    "data": this.filterTabResult( tabNo, resultItem )
                },
                labels: {
                    noRows: "No result found",
                    info: "Page {page} of {pages}",
                }
            });
        }, 100);        
    }


    filterTabResult( tabNo: number, data: any[] ) {
        let filteredData;

        switch (tabNo) {
            case 2:
                filteredData = data.map(item => [item[0], item[3], item[4], ""]);
                break;

            case 3:
                filteredData = data.map(item => [item[9], item[1], item[10], item[5], ""]);
                break;

            case 8:
                filteredData = data.map(item => [item[1], item[2], item[5], ""]);
                break;

            case 9:
                filteredData = data.map(item => [item[0], item[2], item[3], item[4], ""]);
                break;

            default:
                filteredData = data.map(item => {
                    // item.push(""); 
                    return item;
                });
                break;
        }

        return filteredData;
    }


    executeQueries() {
        let elem1 = <HTMLSelectElement> document.getElementById("query_1");
        let elem2 = <HTMLSelectElement> document.getElementById("query_2");
        let opt = <HTMLSelectElement> document.getElementById("operator");

        if (elem1.value === elem2.value) {
            Swal.fire("", "Both value can not be same!", "warning");
            return;
        }

        if(this.isAlreadyProcessed(this.joinQueryForm.value)) {
            Swal.fire("", "Same query is already performed!", "warning");
            return;
        }

        this.loading = true;
        this.jointCount++;

        this.queryItems.push({
            text: `Query ${this.jointCount}`
        });

        let tab1Value = this.searchItems[elem1.selectedIndex - 1];
        let tab2Value = this.searchItems[elem2.selectedIndex - 1];

        if (tab1Value.length === 1) {
            tab1Value[1] = [];
        }

        if (tab2Value.length === 1) {
            tab2Value[1] = [];
        }

        if (this.dataTable99) {
            this.dataTable99.destroy();
        }

        // building first dropdown
        let query1_tabno = 0;
        let query1_tabsplit = [];
        let query1_header = [];

        if (elem1.value.includes("Query")) {
            query1_tabsplit = elem1.value.split(" ");
            query1_tabno = 9 + parseInt(query1_tabsplit[1]);
            query1_header = this.searchHeaders[parseInt(query1_tabsplit[1]) - 1];
        } else {
            query1_tabno = this.tabItems[elem1.selectedIndex - 1];
        }

        // building second dropdown
        let query2_tabno = 0;
        let query2_tabsplit = [];
        let query2_header = [];
        if (elem2.value.includes("Query")) {
            query2_tabsplit = elem2.value.split(" ");
            query2_tabno = 9 + parseInt(query2_tabsplit[1]);
            query2_header = this.searchHeaders[parseInt(query2_tabsplit[1]) - 1];
        } else {
            query2_tabno = this.tabItems[elem2.selectedIndex - 1];
        }


        this.ds.postApiData(this.config.getProcessQueriesUrl(), {
            'query_1_tab'  : query1_tabno,
            'query_1'      : tab1Value,
            'query1_header': query1_header,
            'query_2_tab'  : query2_tabno,
            'query_2'      : tab2Value,
            'query2_header': query2_header,
            'operator'     : opt.value
        })
        .then((resp:any) => {
            let resultItem: any = {};
            resultItem.result = [];
            this.jointQueryResultTotal = 0;    
            this.processedQueryParams.push(this.joinQueryForm.value);     

            if( resp.result.length ) {
                if (resp.result[0][0] instanceof Array) {
                    resp.result.map(item => {
                        if (item.length) {
                            resultItem.result.push(item[0]);
                            this.jointQueryResultTotal++;
                        }
                    });
                } else {
                    resp.result.map(item => {
                        if (item.length) {
                            resultItem.result.push(item);
                            this.jointQueryResultTotal++;
                        }
                    });
                }
            } else {
                this.jointQueryResultTotal = 0;
            }

            this.pillItems.push({
                "type": "success",
                "text": `Q${this.jointCount}: ${elem1.value.replace(/ *\([^)]*\) */g, "")} <i class="${this.optIcons[opt.value]}"></i>  ${elem2.value.replace(/ *\([^)]*\) */g, "")} (${this.jointQueryResultTotal})`
            });            

            resultItem.header = resp.header;

            this.jointQueryResult = resultItem;
            this.tabItems.push( this.jointCount + 9 );
            this.searchItems.push(resultItem.result);
            this.searchHeaders.push(resp.header);
            this.tableHeaders.push(resp.header);

            // console.log( this.tabItems, this.searchItems );

            this.loading = false;

            if( this.table1Wrapper ) {
                this.table1Wrapper.classList.remove("d-none");
            }
            this.table2Wrapper.classList.add("d-none");

            window.setTimeout(() => {
                this.dataTable99 = new DataTable("#query-builder-search-result", {
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
            }, 100);
        })
        .catch(err => this.loading = false);  
    }


    isAlreadyProcessed(submittedData: any) {
        let item = this.processedQueryParams.find(params => 
            (params.query_1 === submittedData.query_1) && 
            (params.query_2 === submittedData.query_2) &&
            (params.operator === submittedData.operator) 
        );

        return item ? true : false;
    }

}
