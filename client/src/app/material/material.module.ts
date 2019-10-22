import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatInputModule } from '@angular/material/input';
import { MatRadioModule } from '@angular/material/radio';
import { MatNativeDateModule } from '@angular/material';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatButtonModule } from '@angular/material/button';
import { MatTabsModule } from '@angular/material/tabs';
import { MatTableModule } from '@angular/material/table';


const components = [
  MatInputModule,
  MatRadioModule,
  MatNativeDateModule,
  MatDatepickerModule,
  MatButtonModule,
  MatTabsModule,
  MatTableModule,
];


@NgModule({
  declarations: [],
  imports: [
    CommonModule,
    ...components,
  ],
  exports: components,
})
export class MaterialModule { }
