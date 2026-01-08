import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AccordionModule } from 'primeng/accordion';
import { FloatLabelModule } from 'primeng/floatlabel';
import { ButtonModule } from 'primeng/button';
import { MenubarModule } from 'primeng/menubar';
import { MenuItem, MessageService } from 'primeng/api';
import { CommonModule } from '@angular/common';
import { ToastModule } from 'primeng/toast';
import { InputTextModule } from 'primeng/inputtext';
import { JobFilters } from '../../models/filters/job-filters';

@Component({
  selector: 'app-jobs-filters',
  imports: [
    FormsModule,
    AccordionModule,
    FloatLabelModule,
    ButtonModule,
    MenubarModule,
    CommonModule,
    ToastModule,
    InputTextModule,
  ],
  providers: [MessageService],
  templateUrl: './jobs-filters.html',
  styleUrl: './jobs-filters.scss',
})
export class JobsFilters {
  @Input() sideFilterActive: boolean = false;
  @Input({ required: true }) totalSearchResults: number = 0;

  @Output() searchEvent = new  EventEmitter<JobFilters>(); 

  filters: JobFilters;

  items: MenuItem[] | undefined;
  searchValue: string = '';

  constructor(private messageService: MessageService) {
     this.filters={}
  }

  ngOnInit() {
    this.items = [
      {
        label: 'File',
        icon: 'pi pi-file',
        items: [
          {
            label: 'New',
            icon: 'pi pi-plus',
            command: () => {
              this.messageService.add({
                severity: 'success',
                summary: 'Success',
                detail: 'File created',
                life: 3000,
              });
            },
          },
          {
            label: 'Print',
            icon: 'pi pi-print',
            command: () => {
              this.messageService.add({
                severity: 'error',
                summary: 'Error',
                detail: 'No printer connected',
                life: 3000,
              });
            },
          },
        ],
      },
      {
        label: 'Search',
        icon: 'pi pi-search',
        command: () => {
          this.messageService.add({
            severity: 'warn',
            summary: 'Search Results',
            detail: 'No results found',
            life: 3000,
          });
        },
      },
      {
        separator: true,
      },
      {
        label: 'Sync',
        icon: 'pi pi-cloud',
        items: [
          {
            label: 'Import',
            icon: 'pi pi-cloud-download',
            command: () => {
              this.messageService.add({
                severity: 'info',
                summary: 'Downloads',
                detail: 'Downloaded from cloud',
                life: 3000,
              });
            },
          },
          {
            label: 'Export',
            icon: 'pi pi-cloud-upload',
            command: () => {
              this.messageService.add({
                severity: 'info',
                summary: 'Shared',
                detail: 'Exported to cloud',
                life: 3000,
              });
            },
          },
        ],
      },
    ];
  }


  emitSearchEvent(){
    this.searchEvent.emit(this.filters)
  }

   clearFilters(){
    // this.filters ={}
  }

}
