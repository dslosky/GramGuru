import { ModuleWithProviders } from '@angular/core';
import { Routes, RouterModule }   from '@angular/router';

import { AppComponent } from './app.component';
import { AdminComponent } from './pages/admin/admin.component';
import { LandingComponent } from './pages/landing/landing.component';
import { UserComponent } from './pages/user/user.component';
import { LoginComponent } from './pages/login/login.component';
import { PurchaseComponent } from './pages/purchase/purchase.component';

import { LoginGuard, AdminGuard } from './auth.service'

const appRoutes: Routes = [
        {
            path: '',
            redirectTo: 'landing',
            pathMatch: 'full'
        },
        {
            path: '',
            component: LandingComponent
        },
        {
            path: 'login',
            component: LoginComponent
        },
        {
            path: 'theguru',
            component: UserComponent,
            canActivate: [LoginGuard]
        },
        {
            path: 'purchase',
            component: PurchaseComponent,
            canActivate: [LoginGuard]
        },
        {
            path: 'admin',
            canActivate: [AdminGuard],
            component: AdminComponent
        }
    ];

// admin and login guards
export const appRoutingProviders: any[] = [
    LoginGuard,
    AdminGuard
];

export const routing: ModuleWithProviders = RouterModule.forRoot(appRoutes);
