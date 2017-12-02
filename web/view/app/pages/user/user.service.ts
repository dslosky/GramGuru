import { Injectable } from '@angular/core';
import { Http, Headers } from '@angular/http';

import { LoginService } from '../login/login.service';

@Injectable()
export class UserService {
    public data: any = null;
    public user: any = null;
    constructor(private http: Http,
                private loginService: LoginService) {}

    getData() {
        return this.http.get('/user-data/' + this.loginService.user.username)
                        .subscribe((res: any) => {
                            res = res.json();
                            this.data = res.data;
                            this.user = res.user;
                        });
    }
}
  

