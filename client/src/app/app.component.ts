import { Component } from '@angular/core';
import { EventsService } from './events.service';
import { map } from 'rxjs/operators';


@Component({
  selector: 'app-root',
  template: `
  <div *ngFor="let event of events$ | async"><pre>{{event | json}}</pre></div>
  <app-new-request-form (created)="onNewRequest($event)"></app-new-request-form>
  `,
  styles: []
})
export class AppComponent {
  events$ = this.eventsService.getLatest().pipe(map(data => data['events']));

  constructor(public eventsService: EventsService) {}

  onNewRequest(req) {
    console.log('req', req);
  }
}
