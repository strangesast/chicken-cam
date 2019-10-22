import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class RequestsService {
  getRequests() {
    return this.http.get('/api/requests');
  }

  createRequest() {
    const body = {};
    return this.http.post('/api/requests', body);
  }

  constructor(public http: HttpClient) { }
}
