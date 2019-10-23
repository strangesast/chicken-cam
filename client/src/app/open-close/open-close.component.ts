import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';

@Component({
  selector: 'app-open-close',
  template: `
  <button mat-flat-button color='accent'>Open</button>
  <button mat-flat-button color='accent'>Close</button>
  `,
  styleUrls: ['./open-close.component.scss']
})
export class OpenCloseComponent implements OnInit {
  @Input()
  state = null;
  
  @Output()
  command = new EventEmitter()

  constructor() { }

  ngOnInit() {
  }

}
