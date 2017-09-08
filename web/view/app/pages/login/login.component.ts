import { Component } from '@angular/core';
import { LoginService } from './login.service';

@Component({
  selector: 'login',
  templateUrl: 'app/pages/login/login.component.html',
  styleUrls: ['app/pages/login/login.component.css']
})
export class LoginComponent {
    public username: string = ''
    public password: string = ''
    public tags: string = ''
    public selected: string = 'login'

    constructor(private loginService: LoginService) {}

    login() {
        this.loginService.login(this.username, this.password);
    }

    register() {
        this.loginService.register(this.username, this.password, this.tags)
    }
    
}