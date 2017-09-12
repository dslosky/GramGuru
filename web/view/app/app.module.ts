import { NgModule }       from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HttpModule, JsonpModule } from '@angular/http';
//import {HttpClientModule} from '@angular/common/http';
import { AppComponent } from './app.component';
import { routing, appRoutingProviders} from './app.routing';
import { FormsModule } from '@angular/forms';

import { NavComponent } from './nav/nav.component'

import { LandingComponent } from './pages/landing/landing.component';
import { LoginComponent } from './pages/login/login.component';
import { UserComponent } from './pages/user/user.component';
import { AdminComponent } from './pages/admin/admin.component';
import { PurchaseComponent } from './pages/purchase/purchase.component';

import { LoginService } from './pages/login/login.service';
import { PurchaseService } from './pages/purchase/purchase.service';
import { AdminService } from './pages/admin/admin.service';

@NgModule({
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    routing,
    HttpModule,
    JsonpModule,
    FormsModule
    //HttpClientModule
  ],
  declarations: [
    AppComponent,
    NavComponent,
    LandingComponent,
    LoginComponent,
    UserComponent,
    AdminComponent,
    PurchaseComponent
  ],
  providers: [
    appRoutingProviders,
    LoginService,
    PurchaseService,
    AdminService
  ],
  bootstrap: [ AppComponent ]
})
export class AppModule {
}