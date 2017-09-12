import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs/Observable'
import { AdminService } from './admin.service'
@Component({
  selector: 'admin',
  templateUrl: 'app/pages/admin/admin.component.html',
  styleUrls: ['app/pages/admin/admin.component.css']
})
export class AdminComponent implements OnInit {
    public adminData: any = null;
    public subscriptions: any[] = []
    public date: any = Date
    constructor(public adminService: AdminService) {}
    
    ngOnInit() {
        this.subscriptions.push(Observable.timer(30000, 30000).data.subscribe((data: any) => {
            this.adminData = data
        }));
        this.adminService.getData()
    }
}