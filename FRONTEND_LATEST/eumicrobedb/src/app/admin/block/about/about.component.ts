import { Component, OnInit } from '@angular/core';
import { ConfigService } from "../../../config";
import { HttpClient } from '@angular/common/http';
import { Items, Status } from "../../../_models";
import Swal from 'sweetalert2';

import { FormGroup, FormArray, FormBuilder } from '@angular/forms';
import { DataSharingService } from 'src/app/_services';

@Component({
    selector: 'app-about-block',
    templateUrl: './about.component.html',
    styleUrls: ['./about.component.css']
})
export class AboutComponent implements OnInit {
    form: FormGroup;
    items: FormArray;
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
            items: this.fb.array([])
        });

        this.ds.getApiData(this.config.getAbout())
        .then((data:Items) => {
            data.items.forEach((line: any) => {
                this.addItem( line );
            });

            this.showForm = true;
        })
        .catch(err => this.loading = false);        

        // this.http.get<Items>( this.config.getAbout() )
        // .subscribe(data => {
        //     data.items.forEach((line: any) => {
        //         this.addItem( line );
        //     });

        //     this.showForm = true;
        // }, err => console.log(err));            
    }


    createItem( data ): FormGroup {
        if( data ) {
            return this.fb.group({
                status: data.About_Status,
                line  : data.About_Text
            });
        } else {
            return this.fb.group({
                status: 1,
                line  : ''
            });
        }

    }


    addItem( data = null ): void {
        this.items = this.form.get('items') as FormArray;
        this.items.push(this.createItem( data ));
    }        


    saveContent() {
        this.loading = true;
        let submitted_data = this.form.value;
        let formatted_data = {
            lines: []
        };

        // formatting data
        submitted_data.items.forEach( (line, index) => {
            formatted_data.lines.push( {
                "About_Status": ~~line.status,
                "About_Text"  : line.line,
                "About_Id"    : Number(index + 1)
            } );
        } );

        this.ds.postApiData(this.config.setAbout(), formatted_data)
        .then((resp:Status) => {
            if( resp.status === "SUCCESS" ) {
                Swal.fire("", "Content updated successfully.", "success");
            }
            this.loading = false;
        })
        .catch(err => this.loading = false);        

        // this.http.post<Status>( this.config.setAbout(), formatted_data )
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
