import { Injectable } from '@angular/core';
import { Http, Headers } from '@angular/http';

@Injectable()
export class AdminService {
    constructor(private http: Http) {}
    public data: any = {}
    getData() {
        return this.http.get('/admin/data')
                .subscribe((res: any) => {
                    this.data = res.json()
                });
    }
}