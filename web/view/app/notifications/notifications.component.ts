import { Component, OnInit, OnDestroy } from '@angular/core';
import { NotificationsService, Notification } from './notifications.service';

import { FadeIn } from '../animations';
@Component({
  selector: 'notifications',
  templateUrl: 'app/notifications/notifications.component.html',
  styleUrls: ['app/notifications/notifications.component.css'],
  animations: [FadeIn('fadeIn')]
})
export class NotificationsComponent implements OnInit, OnDestroy {
    public notification: Notification = null
    public showNot: string = 'false';
    private subscriptions: any[] = []
    constructor(private notService: NotificationsService) {
    }

    ngOnInit() {
        this.subscriptions.push(this.notService.notification.subscribe((not: Notification) => {
            this.notification = not
            this.show();
        }));
    }    

    show() {
        this.showNot = 'true';
    }

    close() {
        this.showNot = 'false';
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