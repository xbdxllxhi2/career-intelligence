import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AccordionModule } from 'primeng/accordion';
import { FloatLabelModule } from 'primeng/floatlabel';
import { ButtonModule } from "primeng/button";

@Component({
  selector: 'app-jobs-filters',
  imports: [FormsModule, AccordionModule, FloatLabelModule, ButtonModule],
  templateUrl: './jobs-filters.html',
  styleUrl: './jobs-filters.scss',
})
export class JobsFilters {
  searchValue: string =''

}
