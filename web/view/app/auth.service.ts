import { Injectable } from '@angular/core';
import { Router, CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { LoginService } from './pages/login/login.service';
import { Observable } from "rxjs/Rx";

@Injectable()
export class LoginGuard implements CanActivate {
    constructor(private user: LoginService,
                private router: Router) {}

    canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot):Observable<boolean>|boolean {
        console.log('LoginGuard#canActivate called');
        if (this.user.loggedIn) {
            return true
        }
        // not logged in so redirect to login page
        this.router.navigate(['/login']);
        return false;
    }
}

@Injectable()
export class AdminGuard implements CanActivate {
    constructor(private user: LoginService,
                private router: Router) {}

    canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot):Observable<boolean>|boolean {
        console.log('AdminGuard#canActivate called');
        if (this.user.isAdmin) {
            return true
        }
        // not logged in so redirect to login page
        this.router.navigate(['/login']);
        return false;
    }
}