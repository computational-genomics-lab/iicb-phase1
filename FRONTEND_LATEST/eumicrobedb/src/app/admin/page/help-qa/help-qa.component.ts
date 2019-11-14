import { Component, OnInit } from '@angular/core';
import { FormArray, FormGroup, FormBuilder } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

import { ConfigService } from 'src/app/config';
import { Status, Items } from 'src/app/_models';
import Swal from 'sweetalert2';
import { DataSharingService } from 'src/app/_services';

@Component({
    selector: 'app-help-qa',
    templateUrl: './help-qa.component.html',
    styleUrls: ['./help-qa.component.css']
})
export class HelpQaComponent implements OnInit {
    form: FormGroup;
    items: FormArray;
    formData: any = [];
    showForm: boolean = false;
    loading: boolean = false;
    trackIndex: number = 1;



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

        this.ds.getApiData(this.config.getHelpQAPage())
        .then((data:any) => {

            this.showForm = true;
            let that = this;
            
            Object.keys(data.items).forEach(function(key) {                
                that.addItem( data.items[key] );
            });            

        })
        .catch(err => this.loading = false);        
    }


    createItem( data ) {
        if ( data ) {
            return this.fb.group({
                Status          : data.Status,
                Question_type   : data.Question_Type,
                Question_type_no: data.Question_Type_No,
                qa              : this.setQuestions(data.qa)
            });
        } else {
            return this.fb.group({
                Status          : 1,
                Question_type   : '',
                Question_type_no: this.items.length + 1,
                qa              : this.setQuestions([{question: "", answer: ""}])
            });
        }

    }


    setQuestions(qas) {
        const arr = new FormArray([]);

        qas.forEach((y, index) => {
            arr.push(this.fb.group({
                Question_no     : index + 1,
                Question        : y.Question,
                Answer          : y.Answer,
                Answer_image    : null
            }));
        });

        return arr;
    }


    addItem( data = null ): void {
        this.items = this.form.get('items') as FormArray;
        this.items.push(this.createItem( data ));
    }


    addNewQuestion( control ) {
        control.push(
            this.fb.group({
                Question_no : control.length + 1,
                Question    : '',
                Answer      : '',
                Answer_image: null
            })
        );
    }


    saveContent() {
        this.loading = true;
        const submittedData = this.form.value;
        this.trackIndex = 1;

        let formattedData = {
            lines: []
        };

        // formatting data
        submittedData.items.forEach( (line, index) => {
            let newLine = line.qa.map(qa => (
                {
                    "Question_id": this.trackIndex++,
                    "Question_no": qa.Question_no,
                    "Question": qa.Question,
                    "Answer": qa.Answer,
                    "Answer_image": null
                }
            ));			

            formattedData.lines.push( {
                "Status": ~~line.Status,
                "Question_type": line.Question_type,
                "Question_type_no": line.Question_type_no,
                "qa": newLine
            } );
        } );
				

        this.ds.postApiData(this.config.setHelpQAPage(), formattedData)
        .then((resp:Status) => {
            if( resp.status === "SUCCESS" ) {
                Swal.fire("", "Content updated successfully.", "success");
            }
            this.loading = false;
        })
        .catch(err => this.loading = false);        
    }

}
