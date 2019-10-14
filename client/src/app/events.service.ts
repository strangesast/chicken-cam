import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class EventsService {
  getLatest() {
    return this.http.get(`/api/events`);
  }

  constructor(public http: HttpClient) { }
}
