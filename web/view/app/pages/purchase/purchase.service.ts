import { Injectable } from '@angular/core';
import { Http, Headers } from '@angular/http';

@Injectable()
export class PurchaseService {
    constructor(private http: Http) {}

    purchase(type: string,
                token: string) {
        let headers = new Headers();
        let data: any = {type: type, token: token};
        headers.append('Content-Type', 'application/json');
        return this.http.post('/charge', 
                          JSON.stringify(data), 
                          {headers}
                ).subscribe((res: any) => {
                    res = res.json()
                    if (res.success) {
                        
                        console.log('PURCHASED')
                    }
                });
    }
}