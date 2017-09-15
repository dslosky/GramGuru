import { Injectable } from '@angular/core';
import { Http, Headers } from '@angular/http';

@Injectable()
export class AdminService {
    constructor(private http: Http) {}
    public data: any = {}

    getData() {
        return this.http.get('/admin/data')
                .subscribe((res: any) => {
                    res = res.json()
                    if (res.success) {
                        this.data = res.admin_data
                    }
                });
    }

    runJob(jobID: number) {
        let headers = new Headers();
        let data: any = {jobID: jobID}
        headers.append('Content-Type', 'application/json');
        return this.http.post('/admin/run-job', 
                            JSON.stringify(data), 
                            {headers}
                    ).subscribe((res: any) => {
                        res = res.json()
                        if (res.success) {
                            console.log('SUCCESS');
                        }
                    });
    }

    resolveError(jobID: number) {
        let headers = new Headers();
        let data: any = {jobID: jobID}
        headers.append('Content-Type', 'application/json');
        return this.http.post('/admin/resolve-error', 
                            JSON.stringify(data), 
                            {headers}
                    ).subscribe((res: any) => {
                        res = res.json()
                        if (res.success) {
                            console.log('SUCCESS')
                        }
                    });
    }
}