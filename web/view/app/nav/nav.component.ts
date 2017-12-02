import { Component } from '@angular/core';
import { LoginService } from '../pages/login/login.service';

@Component({
  selector: 'nav',
  templateUrl: 'app/nav/nav.component.html',
  styleUrls: ['app/nav/nav.component.css']
})
export class NavComponent {
    constructor(public loginService: LoginService) {}
    
}