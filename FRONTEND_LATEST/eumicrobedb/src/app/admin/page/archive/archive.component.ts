import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormGroup, FormArray, FormBuilder } from '@angular/forms';

import { ConfigService } from "../../../config";
import { Items, Status } from "../../../_models";
import Swal from 'sweetalert2';
import { DataSharingService } from 'src/app/_services';

@Component({
    selector: 'app-archive',
    templateUrl: './archive.component.html',
    styleUrls: ['./archive.component.css']
})
export class ArchiveComponent implements OnInit {
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

        this.ds.getApiData(this.config.getArchivePage())
        .then((data:Items) => {
            data.items.forEach((line: any) => {
                this.addItem( line );
            });

            this.showForm = true;
        })
        .catch(err => this.loading = false);

        // this.http.get<Items>( this.config.getArchivePage() )
        // .subscribe(data => {
        //     data.items.forEach((line: any) => {
        //         this.addItem( line );
        //     });

        //     this.showForm = true;
        // }, err => console.log(err));          
    }

    createItem( data ): FormGroup {
        if( data ) {
            return this.fb.group( {
                status : data.Archive_Status,
                month  : data.Released_On_Month,
                text   : data.Update_Text,
                heading: data.Archive_Heading,
                year   : data.Released_On_Year
            } );
        } else {
            return this.fb.group( {
                status : 1,
                month  : '',
                text   : '',
                heading: '',
                year   : ''
            } );
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
                "Archive_Status"   : ~~line.status,
                "Released_On_Month": line.month,
                "Update_Text"      : line.text,
                "Archive_Id"       : Number(index + 1),
                "Archive_Heading"  : line.heading,
                "Released_On_Year" : line.year
            } );
        } );

        this.ds.postApiData(this.config.setArchivePage(), formatted_data)
        .then((resp:Status) => {
            if( resp.status === "SUCCESS" ) {
                Swal.fire("", "Content updated successfully.", "success");
            }
            this.loading = false;
        })
        .catch(err => this.loading = false);        

        // this.http.post<Status>( this.config.setArchivePage(), formatted_data )
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
