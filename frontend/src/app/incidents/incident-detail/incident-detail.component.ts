import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';

import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatProgressBarModule } from '@angular/material/progress-bar';

import { IncidentApiService } from '../../api/incident-api.service';
import { IncidentResponse } from '../../api/incident.models';

@Component({
  selector: 'app-incident-detail-page',
  standalone: true,
  imports: [CommonModule, RouterLink, MatCardModule, MatButtonModule, MatProgressBarModule],
  templateUrl: './incident-detail.component.html',
})
export class IncidentDetailPageComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly api = inject(IncidentApiService);

  readonly loading = signal(false);
  readonly error = signal<string | null>(null);
  readonly incident = signal<IncidentResponse | null>(null);

  async ngOnInit(): Promise<void> {
    const incidentId = this.route.snapshot.paramMap.get('incidentId');
    if (!incidentId) {
      this.error.set('Missing incident id.');
      return;
    }
    await this.load(incidentId);
  }

  async load(incidentId: string): Promise<void> {
    this.loading.set(true);
    this.error.set(null);
    this.incident.set(null);
    try {
      const incident = await firstValueFrom(this.api.getIncident(incidentId));
      this.incident.set(incident);
    } catch {
      this.error.set('Failed to load incident details.');
    } finally {
      this.loading.set(false);
    }
  }
}

