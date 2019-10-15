import { Component, EventEmitter, Output, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';

@Component({
  selector: 'app-new-request-form',
  template: `
  <form [formGroup]="form">
    <div>
      <mat-radio-group aria-label="Select an option" formControlName="value">
        <mat-radio-button [value]="0">Close</mat-radio-button>
        <mat-radio-button [value]="1">Open</mat-radio-button>
      </mat-radio-group>
    </div>
    <div>
      <mat-form-field>
        <input matInput [min]="minDate" [matDatepicker]="picker" placeholder="Choose a date" formControlName="date">
        <mat-datepicker-toggle matSuffix [for]="picker"></mat-datepicker-toggle>
        <mat-datepicker #picker></mat-datepicker>
      </mat-form-field>
    </div>
    <div>
      <app-time-select formControlName="time"></app-time-select>
    </div>
    <button mat-flat-button color="primary" [disabled]="!form.touched || form.invalid" type="submit">Create</button>
  </form>
  <pre>{{form.value | json}}</pre>
  `,
  styleUrls: ['./new-request-form.component.scss']
})
export class NewRequestFormComponent implements OnInit {
  form: FormGroup = this.fb.group({
    value: [0],
    date: [new Date()],
    time: [''],
  });

  @Output()
  created = new EventEmitter();

  constructor(public fb: FormBuilder) { }

  ngOnInit() {
    this.form.valueChanges.subscribe(v => console.log(v));
  }

}
