import { Component, OnInit, Input, forwardRef } from '@angular/core';
import { FormGroup, FormBuilder, FormControl, ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';
import { of, timer, Subject } from 'rxjs';
import { map, switchMap, takeUntil } from 'rxjs/operators';

@Component({
  selector: 'app-time-select',
  template: `
  <form [formGroup]="form">
    <mat-radio-group class="group" aria-label="Select an time" formControlName="value">
      <mat-radio-button class="group_child" *ngFor="let time of defaultTimes" [value]="time">{{time}}</mat-radio-button>
      <mat-radio-button class="group_child" [value]="'now'">Now</mat-radio-button>
      <mat-radio-button class="group_child" [value]="'custom'">Custom</mat-radio-button>
    </mat-radio-group>
    <div class="custom-input" *ngIf="customEnabled">
      <label>Custom Time:</label>
      <mat-form-field>
        <input matInput formControlName="customValue" type="time"/>
      </mat-form-field>
    </div>
  </form>
  `,
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => TimeSelectComponent),
      multi: true,
    }
  ],
  styleUrls: ['./time-select.component.scss']
})
export class TimeSelectComponent implements OnInit, ControlValueAccessor {
  get customEnabled() {
    return this.form.get('value').value == 'custom';
  }

  form: FormGroup = this.fb.group({
    value: ['custom'],
    customValue: [],
  });

  @Input()
  defaultTimes = ['08:00', '09:00', '18:00'];

  hasError = false;

  private _onTouched = (val) => {};
  private _onChanged = (val) => {};

  constructor(private fb: FormBuilder) { }

  ngOnInit() {
    this.form.valueChanges.pipe(
      switchMap(({value, customValue}) => {
        switch (value) {
          case 'custom':
            return of(customValue);
          case 'now': {
            return timer(0, 60*1000).pipe(map(() => {
              const t = new Date();
              const [h, m] = [t.getHours(), t.getMinutes()].map(v => ('0' + v).slice(-2));
              return h + ':' + m;
            }));
          }
          default:
            return of(value);
        }
      }),
      takeUntil(this.destroyed$),
    ).subscribe(v => this._onChanged(v))
  }

  validate(c: FormControl) {
    return (!this.hasError) ? null : {
      invalidTimeError: {
        valid: false,
      },
    };
  }

  writeValue(value: string) {
    if (this.defaultTimes.includes(value)) {
      this.form.patchValue({value}, {emitEvent: false});
    } else {
      this.form.patchValue({value: 'custom', customValue: value}, {emitEvent: false});
    }
  }

  registerOnChange(fn) {
    this._onChanged = fn;
  }

  registerOnTouched(fn) {
    this._onTouched = fn;
  }

  setDisabledState(isDisabled: boolean) {
  }

  destroyed$ = new Subject()
}
