import { Routes } from '@angular/router';
import { IncidentsListPageComponent } from './incidents/incident-list/incidents-list.component';
import { IncidentSubmitPageComponent } from './incidents/incident-submit/incident-submit.component';
import { IncidentDetailPageComponent } from './incidents/incident-detail/incident-detail.component';


export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'incidents' },
  { path: 'incidents', component: IncidentsListPageComponent },
  { path: 'incidents/new', component: IncidentSubmitPageComponent },
  { path: 'incidents/:incidentId', component: IncidentDetailPageComponent },
  { path: '**', redirectTo: 'incidents' },
];
