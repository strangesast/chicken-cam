import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';

@Component({
  selector: 'app-open-close',
  template: `
  <button mat-stroked-button>Open</button>
  <button mat-stroked-button>Close</button>
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
