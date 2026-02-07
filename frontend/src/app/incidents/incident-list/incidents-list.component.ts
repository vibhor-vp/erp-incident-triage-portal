import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatTableModule } from '@angular/material/table';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';

import {
  ERP_MODULES,
  INCIDENT_STATUSES,
  SEVERITIES,
  IncidentStatus,
} from '../../api/incident.models';
import { IncidentsStore } from '../incidents.store';

@Component({
  selector: 'app-incidents-list-page',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    MatCardModule,
    MatFormFieldModule,
    MatSelectModule,
    MatButtonModule,
    MatTableModule,
    MatProgressBarModule,
    MatSnackBarModule,
  ],
  templateUrl: './incidents-list.component.html',
})
export class IncidentsListPageComponent implements OnInit {
  readonly store = inject(IncidentsStore);
  private readonly snackBar = inject(MatSnackBar);

  readonly severities = SEVERITIES;
  readonly modules = ERP_MODULES;
  readonly statuses = INCIDENT_STATUSES;

  readonly displayedColumns = [
    'title',
    'created_at',
    'erp_module',
    'environment',
    'business_unit',
    'severity',
    'category',
    'status',
  ];

  ngOnInit(): void {
    void this.store.load();
  }

  onFilterChange(partial: { severity?: string; erp_module?: string; status?: string }): void {
    this.store.setFilters(partial);
    void this.store.load();
  }

  onClear(): void {
    this.store.clearFilters();
    void this.store.load();
  }

  async onStatusChange(incidentId: string, status: IncidentStatus): Promise<void> {
    try {
      await this.store.updateStatus(incidentId, status);
      this.snackBar.open('Status updated', 'OK', { duration: 2000 });
    } catch {
      this.snackBar.open('Failed to update status', 'OK', { duration: 3000 });
    }
  }
}
