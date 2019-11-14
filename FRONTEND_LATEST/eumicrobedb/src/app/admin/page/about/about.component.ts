import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormGroup, FormArray, FormBuilder } from '@angular/forms';

import { ConfigService } from "../../../config";
import { Items, Status } from "../../../_models";
import Swal from 'sweetalert2';
import { DataSharingService } from 'src/app/_services';


@Component({
    selector: 'app-about-page',
    templateUrl: './about.component.html',
    styleUrls: ['./about.component.css']
})
export class AboutComponent implements OnInit {
    form: FormGroup;
    items: FormArray;
    showForm: boolean = false;
    loading: boolean = false;
    categories = [
        "",
        "Principal Investigator",
        "Graduate Students",
        "Masters Students",
    ];
    defaultFolder = this.config.getMediaUrl().aboutUs;
    defaultPhoto = "default.jpg";

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

        this.ds.getApiData(this.config.getAboutPage())
        .then(async (data:Items) => {
            const promises = [];

            data.items.forEach((line: any) => {
                let photoUrl = this.defaultFolder + line.AboutUs_Id + ".jpg?" + Date.now();
                promises.push(this.getBase64ImageFromUrl(photoUrl).then(base64 => base64));
            });

            const [...datas] = await Promise.all(promises);

            data.items.forEach((line: any, index: number) => {
                let item = {
                    "Person_ContactInfo" : line.Person_ContactInfo,
                    "AboutUs_Type_Name"  : line.AboutUs_Type_Name,
                    "AboutUs_Status"     : line.AboutUs_Status,
                    "AboutUs_Type_No"    : line.AboutUs_Type_No,
                    "Person_Brief_Bio"   : line.Person_Brief_Bio,
                    "Person_Interests"   : line.Person_Interests,
                    "AboutUs_Person_Name": line.AboutUs_Person_Name,
                    "AboutUs_Id"         : line.AboutUs_Id,
                    "photo"              : datas[index]
                };

                this.addItem(item);
            });

            this.showForm = true;
        })
        .catch(err => this.showForm = true);

        // this.http.get<Items>(this.config.getAboutPage())
        // .subscribe(async data => {
        //     const promises = [];

        //     data.items.forEach((line: any) => {
        //         let photoUrl = this.defaultFolder + line.AboutUs_Id + ".jpg?" + Date.now();
        //         promises.push(this.getBase64ImageFromUrl(photoUrl).then(base64 => base64));
        //     });

        //     const [...datas] = await Promise.all(promises);

        //     data.items.forEach((line: any, index: number) => {
        //         let item = {
        //             "Person_ContactInfo" : line.Person_ContactInfo,
        //             "AboutUs_Type_Name"  : line.AboutUs_Type_Name,
        //             "AboutUs_Status"     : line.AboutUs_Status,
        //             "AboutUs_Type_No"    : line.AboutUs_Type_No,
        //             "Person_Brief_Bio"   : line.Person_Brief_Bio,
        //             "Person_Interests"   : line.Person_Interests,
        //             "AboutUs_Person_Name": line.AboutUs_Person_Name,
        //             "AboutUs_Id"         : line.AboutUs_Id,
        //             "photo"              : datas[index]
        //         };

        //         this.addItem(item);
        //     });

        //     this.showForm = true;
        // }, err => console.log(err));
    }


    createItem(data): FormGroup {
        if (data) {
            return this.fb.group({
                type_no: data.AboutUs_Type_No,
                interest: data.Person_Interests,
                status: data.AboutUs_Status,
                email: data.Person_ContactInfo,
                bio: data.Person_Brief_Bio,
                person: data.AboutUs_Person_Name,
                photo: data.photo
            });
        } else {
            return this.fb.group({
                type_no: '',
                interest: '',
                status: 1,
                email: '',
                bio: '',
                person: '',
                photo: "data:image/jpeg;base64,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"
            });
        }
    }


    addItem(data = null): void {
        this.items = this.form.get('items') as FormArray;
        this.items.push(this.createItem(data));
    }


    get item(): any {
        return this.form.get('item');
    }


    openImage(e: Event) {
        let target = <HTMLButtonElement>e.target;
        let fileElem = <HTMLInputElement>target.nextSibling;
        fileElem.click();
    }


    convertImage(e: Event) {
        let target = <HTMLInputElement>e.target;
        let photoElem = <HTMLInputElement>target.nextSibling;
        let imageElem = <HTMLImageElement>target.previousSibling.previousSibling;
        let file = target.files[0];
        let base64Str = "";
        let tableRowIndex = target.closest("tr").rowIndex;
        let reader = new FileReader();

        reader.onloadend = (function (base64Str, items) {
            let base64 = <string>reader.result;
            base64Str = <string>reader.result;
            imageElem.setAttribute("src", base64);
            // photoElem.value = base64.split(";base64,")[1];

            return function (e) {
                items.value[tableRowIndex - 1].photo = e.target.result;
            }
        })(base64Str, this.items);
        reader.readAsDataURL(file);
    }


    async getBase64ImageFromUrl(imageUrl) {
        var res = await fetch(imageUrl);
        var blob = await res.blob();

        return new Promise((resolve, reject) => {
            var reader = new FileReader();
            reader.addEventListener("load", function () {
                resolve(reader.result);
            }, false);

            reader.onerror = () => {
                return reject(this);
            };
            reader.readAsDataURL(blob);
        })
    }

    async saveContent() {
        this.loading = true;
        let submitted_data = this.form.value;
        let formatted_data = {
            lines: []
        };

        submitted_data.items.forEach((line, index) => {
            let photoUrl = line.photo.split(";base64,")[1];

            formatted_data.lines.push({
                "Person_Photo": `${photoUrl}\n`,
                "AboutUs_Type_No": Number(line.type_no),
                "Person_Interests": line.interest,
                "AboutUs_Status": ~~line.status,
                "AboutUs_Type_Name": this.categories[line.type_no],
                "Person_ContactInfo": line.email,
                "Person_Brief_Bio": line.bio,
                "AboutUs_Id": Number(index + 1),
                "AboutUs_Person_Name": line.person
            });

        });

        this.ds.postApiData(this.config.setAboutPage(), formatted_data)
        .then((resp:Status) => {
            if( resp.status === "SUCCESS" ) {
                Swal.fire("", "Content updated successfully.", "success");
            }
            this.loading = false;
        })
        .catch(err => this.loading = false);

        // this.http.post<Status>(this.config.setAboutPage(), formatted_data)
        // .subscribe(resp => {
        //     if (resp.status === "SUCCESS") {
        //         Swal.fire("", "Content updated successfully.", "success");
        //     }
        //     this.loading = false;
        // }, error => {
        //     console.log(error);
        // });

    }
}
