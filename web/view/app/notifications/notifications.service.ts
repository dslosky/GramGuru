import { Injectable } from '@angular/core';
import { ReplaySubject } from 'rxjs/ReplaySubject';

@Injectable()
export class NotificationsService {
    public notification = new ReplaySubject(1);
    
    success(title:string,
            message:string='') {
        var not: Notification = {type: 'success',
                                    title: title,
                                    message:message}
        this.notification.next(not)
    }

    warning(title:string,
            message:string='') {
        var not: Notification = {type: 'warning',
                                    title: title,
                                    message:message}
        this.notification.next(not)
    }

    info(title:string,
            message:string='') {
        var not: Notification = {type: 'info',
                                    title: title,
                                    message:message}
        this.notification.next(not)
    }
}

export interface Notification {
    type: string;
    title: string;
    message: string;
}