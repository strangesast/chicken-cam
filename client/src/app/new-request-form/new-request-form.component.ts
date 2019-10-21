import { Component, EventEmitter, Output, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';


function formatTime(d) {
  return [d.getHours(), d.getMinutes()].map(g => ('0' + g).slice(-2)).join(':');
}

@Component({
  selector: 'app-new-request-form',
  template: `
  <form [formGroup]="form" (submit)="onSubmit()">
    <label>Command:</label>
    <mat-radio-group class="group" aria-label="Select an option" formControlName="value">
      <mat-radio-button class="group_child" [value]="0">Close</mat-radio-button>
      <mat-radio-button class="group_child" [value]="1">Open</mat-radio-button>
    </mat-radio-group>
    <label>Date:</label>
    <div class="group">
      <mat-form-field class="group_child">
        <input matInput [min]="minDate" [matDatepicker]="picker" placeholder="Choose a date" formControlName="date">
        <mat-datepicker-toggle matSuffix [for]="picker"></mat-datepicker-toggle>
        <mat-datepicker #picker></mat-datepicker>
      </mat-form-field>
      <button mat-stroked-button class="group_child" [disabled]="isToday()" (click)="setDateToday()">Today</button>
    </div>
    <label>Time</label>
    <app-time-select formControlName="time"></app-time-select>
    <button mat-flat-button color="primary" [disabled]="!form.touched || form.invalid" type="submit">Create</button>
  </form>
  <pre>{{form.value | json}}</pre>
  `,
  styleUrls: ['./new-request-form.component.scss']
})
export class NewRequestFormComponent implements OnInit {
  form: FormGroup = this.fb.group((d => ({
    value: [],
    date: [d],
    time: [formatTime(d)],
  }))(new Date()));

  @Output()
  created = new EventEmitter();

  isToday() {
    const [a, b] = [this.form.get('date').value, new Date()].map(v => v.toISOString().slice(0, 10));
    return a == b;
  }

  setDateToday() {
    this.form.patchValue({date: new Date()});
  }

  onSubmit() {
    if (this.form.valid) {
      const {value,date,time} = this.form.value;
      const [h,m] = time.split(':').map(g => parseInt(g, 10));
      date.setMinutes(m);
      date.setHours(h);
      this.created.emit({date, value});
    }
  }

  ngOnInit() {
    // this.form.valueChanges.subscribe(v => console.log(v));
  }

  constructor(public fb: FormBuilder) { }

}
