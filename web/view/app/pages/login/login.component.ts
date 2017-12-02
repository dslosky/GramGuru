import { Component, ChangeDetectorRef } from '@angular/core';
import { LoginService } from './login.service';
import { NotificationsService } from '../../notifications/notifications.service';

@Component({
  selector: 'login',
  templateUrl: 'app/pages/login/login.component.html',
  styleUrls: ['app/pages/login/login.component.css']
})
export class LoginComponent {
    public username: string = ''
    public password: string = ''
    public email: string = ''
    public selected: string = 'register'

    constructor(private loginService: LoginService,
                private notificationsService: NotificationsService,
                private changeDetector: ChangeDetectorRef) {}

    login() {
        this.loginService.login(this.username, this.password);
        this.changeDetector.detectChanges();
    }

    register() {
        let valid = this.validate('register')
        if (valid) {
            this.loginService.register(this.username, this.password, this.email);
            this.changeDetector.detectChanges();
        }
    }

    validate(vtype: string) {
        if (vtype == 'register') {
            if (!this.email) {
                this.notificationsService.warning('Invalid Credentials', 'Email is required')
                return false;
            }
        }

        if (!this.username) {
            this.notificationsService.warning('Invalid Credentials', 'Username is required')
            return false;
        } else if (!this.password) {
            this.notificationsService.warning('Invalid Credentials', 'Password is required')
            return false;
        }
        return true;
    } 
    
}