import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';

import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';

import { firstValueFrom } from 'rxjs';

import { IncidentApiService } from '../../api/incident-api.service';
import { ENVIRONMENTS, ERP_MODULES, IncidentCreateRequest } from '../../api/incident.models';

@Component({
  selector: 'app-incident-submit-page',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatSnackBarModule,
  ],
  templateUrl: './incident-submit.component.html',
})
export class IncidentSubmitPageComponent {
  private readonly fb = inject(FormBuilder);
  private readonly api = inject(IncidentApiService);
  private readonly router = inject(Router);
  private readonly snackBar = inject(MatSnackBar);

  readonly modules = ERP_MODULES;
  readonly environments = ENVIRONMENTS;

  submitting = false;

  readonly form = this.fb.nonNullable.group({
    title: ['', [Validators.required, Validators.minLength(5)]],
    description: ['', [Validators.required, Validators.minLength(10)]],
    erp_module: ['', [Validators.required]],
    environment: ['', [Validators.required]],
    business_unit: ['', [Validators.required]],
  });

  async onSubmit(): Promise<void> {
    if (this.form.invalid || this.submitting) return;
    this.submitting = true;

    try {
      const payload = this.form.getRawValue() as unknown as IncidentCreateRequest;
      await firstValueFrom(this.api.createIncident(payload));
      this.snackBar.open('Incident submitted', 'OK', { duration: 2500 });
      await this.router.navigateByUrl('/incidents');
    } catch {
      this.snackBar.open('Failed to submit incident', 'OK', { duration: 3500 });
    } finally {
      this.submitting = false;
    }
  }

  async onCancel(): Promise<void> {
    await this.router.navigateByUrl('/incidents');
  }
}

