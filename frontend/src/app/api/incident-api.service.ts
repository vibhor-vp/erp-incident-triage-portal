import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import {
  IncidentCreateRequest,
  IncidentResponse,
  IncidentStatus,
} from './incident.models';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class IncidentApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = environment.apiBaseUrl;

  listIncidents(filters?: {
    severity?: string;
    erp_module?: string;
    status?: string;
  }): Observable<IncidentResponse[]> {
    let params = new HttpParams();
    if (filters?.severity) params = params.set('severity', filters.severity);
    if (filters?.erp_module) params = params.set('erp_module', filters.erp_module);
    if (filters?.status) params = params.set('status', filters.status);

    return this.http.get<IncidentResponse[]>(`${this.baseUrl}/incidents`, { params });
  }

  createIncident(payload: IncidentCreateRequest): Observable<IncidentResponse> {
    return this.http.post<IncidentResponse>(`${this.baseUrl}/incidents`, payload);
  }

  updateIncidentStatus(
    incidentId: string,
    status: IncidentStatus
  ): Observable<IncidentResponse> {
    return this.http.patch<IncidentResponse>(
      `${this.baseUrl}/incidents/${encodeURIComponent(incidentId)}/status`,
      { status }
    );
  }
}
