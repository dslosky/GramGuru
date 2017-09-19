import { Component } from '@angular/core';
import { LoginService } from './pages/login/login.service';

@Component({
  selector: 'my-app',
  templateUrl: 'app/app.component.html',
  styleUrls: ['app/app.component.css']
})
export class AppComponent {
    constructor(loginService: LoginService) {
        loginService.checkLoggedIn();
    }
    
}