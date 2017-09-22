import { Injectable } from '@angular/core';
import { Http, Headers } from '@angular/http';
import { Router } from '@angular/router';
import { NotificationsService } from '../../notifications/notifications.service';

@Injectable()
export class LoginService {
    public loggedIn: boolean = false;
    public isAdmin: boolean = false;
    public user: any = null;

    constructor(private http: Http,
                private router: Router,
                public notService: NotificationsService) {}

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
                        this.isAdmin = res.user.type == 'admin';
                        this.user = res.user;
                        
                        this.router.navigate(['/theguru']);
                        this.notService.success('Welcome Back ' + this.user['username']);
                    } else {
                        this.notService.warning(res.msg);
                    }
                });
  }

  register(username: string, password: string, email: string) {
    let headers = new Headers();
    let data: any = {username: username, password: password, email: email}
    headers.append('Content-Type', 'application/json');
    return this.http.post('/register', 
                          JSON.stringify(data), 
                          {headers}
                ).subscribe((res: any) => {
                    res = res.json()
                    if (res.success) {
                        this.loggedIn = true;
                        this.isAdmin = res.user.type == 'admin';
                        this.user = res.user;

                        this.router.navigate(['/theguru']);
                        this.notService.success('Welcome ' + this.user['username'] + '!');
                    } else {
                        this.notService.warning(res.msg);
                    }
                });
  }

  checkLoggedIn() {
    return this.http.get('/logged_in')
                    .subscribe((res: any) => {
                    res = res.json()
                    if (res.loggedIn) {
                        this.loggedIn = true;
                        this.isAdmin = res.user.type == 'admin';
                        this.user = res.user;
                    }
                });
  }

  logout() {
    return this.http.get('/logout')
                    .subscribe((res: any) => {
                    this.router.navigate(['']);
                    this.notService.success(this.user['username'] + ' logged out.');

                    this.loggedIn = false;
                });
  }
  
}

