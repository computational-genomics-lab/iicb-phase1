import { Component, OnInit } from '@angular/core';
import { ConfigService } from "../../../config";
import { HttpClient } from '@angular/common/http';
import { Lines, Status } from "../../../_models";
import Swal from 'sweetalert2';

import { FormGroup, FormArray, FormBuilder } from '@angular/forms';
import { DataSharingService } from 'src/app/_services';

@Component({
    selector: 'app-data-usage-policy',
    templateUrl: './data-usage-policy.component.html',
    styleUrls: ['./data-usage-policy.component.css']
})
export class DataUsagePolicyComponent implements OnInit {
    form: FormGroup;
    lines: FormArray;
    showForm: boolean = false;
    loading: boolean = false;

    constructor(
        private http: HttpClient,
        private config: ConfigService,
        private fb: FormBuilder,
        private ds: DataSharingService
    ) { }

    
    ngOnInit() {
        this.form = this.fb.group({
            lines: this.fb.array([])
        });

        this.ds.getApiData(this.config.getDataUsagePolicy())
        .then((data:Lines) => {
            data.lines.forEach((line: any) => {
                this.addItem( line );
            });

            this.showForm = true;
        })
        .catch(err => this.loading = false);

        // this.http.get<Lines>( this.config.getDataUsagePolicy() )
        // .subscribe(data => {
        //     data.lines.forEach((line: any) => {
        //         this.addItem( line );
        //     });

        //     this.showForm = true;
        // }, err => console.log(err));        
    }


    createItem( data ): FormGroup {
        if( data ) {
            return this.fb.group({
                status: data.Line_Status,
                line  : data.Line_Text
            });
        } else {
            return this.fb.group({
                status: 1,
                line  : ''
            });
        }

    }


    addItem( data = null ): void {
        this.lines = this.form.get('lines') as FormArray;
        this.lines.push(this.createItem( data ));
    }    


    saveContent() {
        this.loading = true;
        let submitted_data = this.form.value;
        let formatted_data = {
            lines: []
        };

        // formatting data
        submitted_data.lines.forEach( (line, index) => {
            formatted_data.lines.push( {
                "Line_Status": ~~line.status,
                "Line_Text"  : line.line,
                "Line_No"    : Number(index + 1)
            } );
        } );

        this.ds.postApiData(this.config.setDataUsagePolicy(), formatted_data)
        .then((resp:Status) => {
            if( resp.status === "SUCCESS" ) {
                Swal.fire("", "Content updated successfully.", "success");
            }
            this.loading = false;
        })
        .catch(err => this.loading = false);         

        // this.http.post<Status>( this.config.setDataUsagePolicy(), formatted_data )
        // .subscribe( resp => { 
        //     if( resp.status === "SUCCESS" ) {
        //         Swal.fire("", "Content updated successfully.", "success");
        //     }
        //     this.loading = false;
        // }, error => {
        //     console.log( error ); 
        // } );        
    }
}
