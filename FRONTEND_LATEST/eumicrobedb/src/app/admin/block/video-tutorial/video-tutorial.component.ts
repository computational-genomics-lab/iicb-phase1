import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormGroup, FormArray, FormBuilder } from '@angular/forms';

import Swal from 'sweetalert2';

import { ConfigService } from "../../../config";
import { Items, Lines, Status } from "../../../_models";
import { DataSharingService } from 'src/app/_services';

@Component({
    selector: 'app-video-tutorial',
    templateUrl: './video-tutorial.component.html',
    styleUrls: ['./video-tutorial.component.css']
})
export class VideoTutorialComponent implements OnInit {
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

        this.ds.getApiData(this.config.getVideoTutorials())
        .then((data:Items) => {
            data.items.forEach((line: any) => {
                this.addItem( line );
            });

            this.showForm = true;
        })
        .catch(err => this.loading = false);

        // this.http.get<Items>( this.config.getVideoTutorials() )
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
                video_status: data.video_status,
                video_title : data.video_title,
                video_link  : data.video_link
            });
        } else {
            return this.fb.group({
                video_status: 1,
                video_title : '',
                video_link  : ''
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
                "video_status": ~~line.video_status,
                "video_title" : line.video_title,
                "video_link"  : line.video_link,
                "video_id"    : Number(index + 1)
            } );
        } );

        this.ds.postApiData(this.config.setVideoTutorials(), formatted_data)
        .then((resp:Status) => {
            if( resp.status === "SUCCESS" ) {
                Swal.fire("", "Content updated successfully.", "success");
            }
            this.loading = false;
        })
        .catch(err => this.loading = false);        

        // this.http.post<Status>( this.config.setVideoTutorials(), formatted_data )
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
