import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class DataSharingService {

    public isUserLoggedIn: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);

    constructor() {
        this.isUserLoggedIn.next( localStorage.getItem("currentUser") ? true : false);
    }

    getApiData(url: string, returnType:string = "json") {
        return new Promise((resolve, reject) => {
            fetch(url)
            .then(data => {
                // TODO: Return type for GET method can be implemented here
                switch(returnType) {
                    case "json":
                        return data.json();
                    default:
                        return data.text();
                }
            })
            .then(resp => resolve(resp))
            .catch(err => reject(err));
        });
    }


    postApiData(url: string, postData:any = {}, returnType:string = "json" ) {
        return new Promise((resolve, reject) => {
            fetch(url, {
                method: "post",
                body: JSON.stringify(postData)
            })
            .then(data => {
                // TODO: Return type for POST method can be implemented here
                return data.json();
            })
            .then(resp => resolve(resp))
            .catch(err => reject(err));
        });        
    }


    formApiData(url: string, postData:any = {}) {
        return new Promise((resolve, reject) => {
            fetch(url, {
                method: "post",
                body: postData
            })
            .then(data => {
                return data.json();
            })
            .then(resp => resolve(resp))
            .catch(err => reject(err));
        });
    }
}
