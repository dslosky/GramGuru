import { Component, OnInit, OnDestroy, ChangeDetectorRef } from '@angular/core';
import { Observable } from 'rxjs/Observable'
import 'rxjs/add/observable/timer';
import { AdminService } from './admin.service'
@Component({
  selector: 'admin',
  templateUrl: 'app/pages/admin/admin.component.html',
  styleUrls: ['app/pages/admin/admin.component.css']
})
export class AdminComponent implements OnInit, OnDestroy {
    public subscriptions: any[] = []
    public date: any = Date
    public Math: any = Math;
    constructor(public adminService: AdminService,
                private changeDetector: ChangeDetectorRef) {}
    
    ngOnInit() {
        this.subscriptions.push(Observable.timer(1, 10000).subscribe((data: any) => {
            this.adminService.getData();
            this.changeDetector.detectChanges()
        }));
    }

    ngOnDestroy() {
        this.endSubscriptions()
    }

    endSubscriptions() {
        for (var sub in this.subscriptions) {
            this.subscriptions[sub].unsubscribe()
        }
    }
}