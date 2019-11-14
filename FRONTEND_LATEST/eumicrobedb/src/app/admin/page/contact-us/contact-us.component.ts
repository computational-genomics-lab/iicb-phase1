import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormGroup, FormArray, FormBuilder } from '@angular/forms';

import Swal from 'sweetalert2';

import { ConfigService } from "../../../config";
import { Items, Lines, Status } from "../../../_models";
import { DataSharingService } from 'src/app/_services';

@Component({
    selector: 'app-contact-us',
    templateUrl: './contact-us.component.html',
    styleUrls: ['./contact-us.component.css']
})
export class ContactUsComponent implements OnInit {
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

        this.ds.getApiData(this.config.getContactPage())
        .then((data:Items) => {
            data.items.forEach((line: any) => {
                this.addItem( line );
            });

            this.showForm = true;
        })
        .catch(err => this.loading = false);

        // this.http.get<Items>( this.config.getContactPage() )
        // .subscribe(data => {
        //     data.items.forEach((line: any) => {
        //         this.addItem( line );
        //     });

        //     this.showForm = true;
        // }, err => console.log(err));         
    }

    createItem( data: any ): FormGroup {
        if( data ) {
            return this.fb.group({
                status: data.ContactUs_Status,
                info_text : data.ContactUs_Info_Text
            });
        } else {
            return this.fb.group({
                status: 1,
                info_text : ''
            });
        }
    }
    
    
    addItem( data = null ): void {
        this.lines = this.form.get('lines') as FormArray;
        this.lines.push( this.createItem( data ) );
    }      


    saveContent() {
        this.loading = true;
        let submitted_data = this.form.value;
        let formatted_data = {
            lines: []
        };

        // formatting data
        submitted_data.lines.forEach( (line: any, index: any ) => {
            formatted_data.lines.push( {
                "ContactUs_Status"   : ~~line.status,
                "ContactUs_Info_Text": line.info_text,
                "ContactUs_Id"       : Number(index + 1)
            } );
        } );

        this.ds.postApiData(this.config.setContactPage(), formatted_data)
        .then((resp:Status) => {
            if( resp.status === "SUCCESS" ) {
                Swal.fire("", "Content updated successfully.", "success");
            }
            this.loading = false;
        })
        .catch(err => this.loading = false);          

        // this.http.post<Status>( this.config.setContactPage(), formatted_data )
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
