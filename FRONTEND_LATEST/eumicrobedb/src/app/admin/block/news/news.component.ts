import { Component, OnInit } from '@angular/core';
import { ConfigService } from "../../../config";
import { HttpClient } from '@angular/common/http';
import { FormGroup, FormArray, FormBuilder } from '@angular/forms';
import Swal from 'sweetalert2';

import { Items, Status } from "src/app/_models";
import { DataSharingService } from 'src/app/_services';

@Component({
    selector: 'app-news',
    templateUrl: './news.component.html',
    styleUrls: ['./news.component.css']
})
export class NewsComponent implements OnInit {
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

        this.ds.getApiData(this.config.getNews())
        .then((data:Items) => {
            data.items.forEach((line: any) => {
                this.addItem( line );
            });

            this.showForm = true;
        })
        .catch(err => this.loading = false);
        
        // this.http.get<Items>( this.config.getNews() )
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
                status: data.Line_Status,
                line  : data.Line_Text,
                format: data.Line_Format
            });
        } else {
            return this.fb.group({
                status: 1,
                line  : '',
                format: '',
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
                "Line_Status": ~~line.status,
                "Line_Text"  : line.line,
                "Line_Format": line.format,
                "Line_No"    : Number(index + 1)
            } );
        } );

        this.ds.postApiData(this.config.setNews(), formatted_data)
        .then((resp:Status) => {
            if( resp.status === "SUCCESS" ) {
                Swal.fire("", "Content updated successfully.", "success");
            }
            this.loading = false;
        })
        .catch(err => this.loading = false);        

        // this.http.post<Status>( this.config.setNews(), formatted_data )
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
