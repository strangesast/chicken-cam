import { Component } from '@angular/core';
import { EventsService } from './events.service';
import { of } from 'rxjs';
import { map } from 'rxjs/operators';

import { RequestsService } from './requests.service';

function formatTime(date: Date) {
  const h = date.getHours();
  const m = date.getMinutes();
  const p = h < 12 ? 'AM' : 'PM';
  return (h == 0 ? 12 : h > 12 ? (h - 12) : h) + ':' + ('0' + m).slice(-2) + ' ' + p;
}

@Component({
  selector: 'app-root',
  template: `
  <div class="container mat-elevation-z2">
    <header>
      <h1>Chicken Cam</h1>
      <p *ngIf="description$ | async as description">Open as of {{description.date}}, {{description.time}}</p>
    </header>
    <mat-tab-group mat-align-tabs="center">
      <mat-tab label="Command">
        <app-open-close></app-open-close>
      </mat-tab>
      <mat-tab label="Schedule">
        <h2 class="header">Schedule New</h2>
        <app-new-request-form (created)="onNewRequest($event)"></app-new-request-form>
        <h2 class="header">Upcoming</h2>
        <div *ngIf="history$ | async as history">
          <table class="table" *ngIf="history$ | async as history" mat-table [dataSource]="history">
            <ng-container matColumnDef="date">
              <th mat-header-cell *matHeaderCellDef>Date</th>
              <td mat-cell *matCellDef="let element">{{element.date}}</td>
            </ng-container>
            <ng-container matColumnDef="value">
              <th mat-header-cell *matHeaderCellDef>Action</th>
              <td mat-cell *matCellDef="let element">{{element.value == '1' ? 'OPEN' : 'CLOSE'}}</td>
            </ng-container>
            <!--
            <ng-container matColumnDef="created">
              <th mat-header-cell *matHeaderCellDef>Created</th>
              <td mat-cell *matCellDef="let element"> {{element.created}} </td>
            </ng-container>
            <ng-container matColumnDef="completed">
              <th mat-header-cell *matHeaderCellDef>Completed</th>
              <td mat-cell *matCellDef="let element">{{element.completed}}</td>
            </ng-container>
            -->
            <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
            <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>
          </table>
        </div>
      </mat-tab>
      <mat-tab label="History">
        <div *ngIf="history$ | async as history">
          <table class="table" *ngIf="history$ | async as history" mat-table [dataSource]="history">
            <ng-container matColumnDef="date">
              <th mat-header-cell *matHeaderCellDef>Date</th>
              <td mat-cell *matCellDef="let element">{{element.date}}</td>
            </ng-container>
            <ng-container matColumnDef="value">
              <th mat-header-cell *matHeaderCellDef>Action</th>
              <td mat-cell *matCellDef="let element">{{element.value == '1' ? 'OPEN' : 'CLOSE'}}</td>
            </ng-container>
            <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
            <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>
          </table>
        </div>
      </mat-tab>
    </mat-tab-group>
  </div>
  `,
  styleUrls: ['./app.component.scss'],
})
export class AppComponent {
  displayedColumns = ['date', 'value'];//, 'created', 'completed'];
  events$ = this.eventsService.getLatest().pipe(map(data => data['events']));

  history$ = this.service.getRequests().pipe(
    map(resp => {
      return resp['records'];
    }),
  );

  description$ = of(null).pipe(
    map(d => {
      const date = new Date();
      const rtf1 = new (Intl as any).RelativeTimeFormat('en', { numeric: 'auto', style: 'long' });
      const days = -1;
      return {date: rtf1.format(days, 'day'), time: formatTime(date)};
    }),
  );

  constructor(public eventsService: EventsService, public service: RequestsService) {}

  onNewRequest(req) {
    console.log('req', req);
  }
}
