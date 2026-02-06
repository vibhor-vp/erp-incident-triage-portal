import { Routes } from '@angular/router';
import { IncidentsListPageComponent } from './incidents/incident-list/incidents-list.component';
import { IncidentSubmitPageComponent } from './incidents/incident-submit/incident-submit.component';


export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'incidents' },
  { path: 'incidents', component: IncidentsListPageComponent },
  { path: 'incidents/new', component: IncidentSubmitPageComponent },
  { path: '**', redirectTo: 'incidents' },
];

