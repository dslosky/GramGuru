import { Component, OnInit } from '@angular/core';
import { AdminService } from './admin.service'
@Component({
  selector: 'admin',
  templateUrl: 'app/pages/admin/admin.component.html',
  styleUrls: ['app/pages/admin/admin.component.css']
})
export class AdminComponent implements OnInit {
    public adminData: any = null;
    public subscriptions: any[] = []
    constructor(public adminService: AdminService) {}
    
    ngOnInit() {
        // this.subscriptions.push(this.adminService.data.subscribe((data: any) => {
        //     this.adminData = data
        // }));
        this.adminService.getData()
    }
}