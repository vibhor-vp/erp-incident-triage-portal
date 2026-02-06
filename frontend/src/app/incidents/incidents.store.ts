import { inject, Injectable, signal } from '@angular/core';
import { firstValueFrom } from 'rxjs';

import { IncidentApiService } from '../api/incident-api.service';
import { IncidentResponse, IncidentStatus } from '../api/incident.models';

type IncidentFilters = {
  severity?: string;
  erp_module?: string;
  status?: string;
};

@Injectable({ providedIn: 'root' })
export class IncidentsStore {
  private readonly api = inject(IncidentApiService);

  readonly incidents = signal<IncidentResponse[]>([]);
  readonly loading = signal(false);
  readonly error = signal<string | null>(null);

  readonly filters = signal<IncidentFilters>({});

  async load(): Promise<void> {
    this.loading.set(true);
    this.error.set(null);
    try {
      const data = await firstValueFrom(this.api.listIncidents(this.filters()));
      this.incidents.set(data);
    } catch (e) {
      this.error.set('Failed to load incidents.');
    } finally {
      this.loading.set(false);
    }
  }

  setFilters(partial: IncidentFilters): void {
    this.filters.update((current) => ({ ...current, ...partial }));
  }

  clearFilters(): void {
    this.filters.set({});
  }

  async updateStatus(incidentId: string, status: IncidentStatus): Promise<void> {
    try {
      const updated = await firstValueFrom(this.api.updateIncidentStatus(incidentId, status));
      this.incidents.update((rows) =>
        rows.map((r) => (r.id === incidentId ? updated : r))
      );
    } catch (e) {
      this.error.set('Failed to update incident status.');
      throw e;
    }
  }
}

