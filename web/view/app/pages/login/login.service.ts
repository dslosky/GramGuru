import { Injectable } from '@angular/core';
import { Http, Headers } from '@angular/http';

@Injectable()
export class LoginService {
    public loggedIn: boolean = false;
    public isAdmin: boolean = false;
    public user: any = null;

    constructor(private http: Http) {}

  login(username: string, password: string) {
    let headers = new Headers();
    let creds: any = {username: username, password: password}
    headers.append('Content-Type', 'application/json');
    return this.http.post('/login', 
                          JSON.stringify(creds), 
                          {headers}
                ).subscribe((res: any) => {
                    res = res.json()
                    if (res.success) {
                        this.loggedIn = true;
                        this.isAdmin = res.user.type == 'admin'
                        this.user = res.user
                        console.log('REDIRECT')
                    }
                });
  }

  register(username: string, password: string, tags: string) {
    let headers = new Headers();
    let data: any = {username: username, password: password, tags: tags}
    headers.append('Content-Type', 'application/json');
    return this.http.post('/register', 
                          JSON.stringify(data), 
                          {headers}
                ).subscribe((res: any) => {
                    res = res.json()
                    if (res.success) {
                        this.loggedIn = true;
                        this.isAdmin = res.user.type == 'admin'
                        this.user = res.user
                        console.log('REGISTERED')
                    }
                });
  }

  checkLoggedIn() {
    return this.http.get('/logged_in')
                    .subscribe((res: any) => {
                    res = res.json()
                    if (res.loggedIn) {
                        this.loggedIn = true;
                        this.isAdmin = res.user.type == 'admin'
                        this.user = res.user
                    }
                });
  }
  
}

