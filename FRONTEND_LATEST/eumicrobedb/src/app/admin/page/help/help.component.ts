import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormGroup, FormArray, FormBuilder } from '@angular/forms';

import { ConfigService } from "../../../config";
import { Lines, Items, Status } from "../../../_models";
import Swal from 'sweetalert2';
import { DataSharingService } from 'src/app/_services';

@Component({
    selector: 'app-help-page',
    templateUrl: './help.component.html',
    styleUrls: ['./help.component.css']
})
export class HelpComponent implements OnInit {
    form: FormGroup;
    items: FormArray;
    showForm: boolean = false;
    loading: boolean = false;
    months = ["January","February","March","April","May","June","July", "August","September","October","November","December"];

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

        this.ds.getApiData(this.config.getHelpPage())
        .then((data:Lines) => {
            data.lines.forEach((line: any) => {
                this.addItem( line );
            });

            this.showForm = true;
        })
        .catch(err => this.loading = false);

        // this.http.get<Lines>( this.config.getHelpPage() )
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
                status        : data.Help_Status,
                heading       : data.Help_Heading,
                question_id   : data.HelpQuesAns_Id,
                released_month: data.Released_On_Month,
                released_year : data.Released_On_Year
            });
        } else {
            return this.fb.group({
                status        : 1,
                heading       : '',
                question_id   : '',
                released_month: '',
                released_year : ''
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
        submitted_data.items.forEach( (line, index) => { console.log(line);
            formatted_data.lines.push( {
                "Help_Status"       : ~~line.status,
                "Help_Heading"      : line.heading,
                "Help_Id"           : Number( index + 1 ),
                "Released_On_Month" : line.released_month,
                "Released_On_Year"  : Number( line.released_year )
            } );
        } );

        this.ds.postApiData(this.config.setHelpPage(), formatted_data)
        .then((resp:Status) => {
            if( resp.status === "SUCCESS" ) {
                Swal.fire("", "Content updated successfully.", "success");
            }
            this.loading = false;
        })
        .catch(err => this.loading = false);         

        // this.http.post<Status>( this.config.setHelpPage(), formatted_data )
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
