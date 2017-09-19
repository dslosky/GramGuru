import { Component, OnInit, OnDestroy, ChangeDetectorRef } from '@angular/core';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/observable/timer';
import { UserService } from './user.service';

@Component({
  selector: 'user',
  templateUrl: 'app/pages/user/user.component.html',
  styleUrls: ['app/pages/user/user.component.css']
})
export class UserComponent implements OnInit, OnDestroy {
    private subscriptions: any[] = [];
    constructor(public userService: UserService,
                private changeDetector: ChangeDetectorRef) {}

    ngOnInit() {
        this.subscriptions.push(Observable.timer(1, 10000).subscribe((data: any) => {
            this.userService.getData();
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