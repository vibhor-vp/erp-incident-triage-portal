export const ERP_MODULES = ['AP', 'AR', 'GL', 'INVENTORY', 'HR', 'PAYROLL'] as const;
export type ERPModule = (typeof ERP_MODULES)[number];

export const ENVIRONMENTS = ['PROD', 'TEST'] as const;
export type Environment = (typeof ENVIRONMENTS)[number];

export const SEVERITIES = ['P1', 'P2', 'P3'] as const;
export type Severity = (typeof SEVERITIES)[number];

export const CATEGORIES = [
  'CONFIGURATION_ISSUE',
  'DATA_ISSUE',
  'INTEGRATION_FAILURE',
  'SECURITY_ACCESS',
  'UNKNOWN',
] as const;
export type Category = (typeof CATEGORIES)[number];

export const INCIDENT_STATUSES = ['OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED'] as const;
export type IncidentStatus = (typeof INCIDENT_STATUSES)[number];

export interface IncidentCreateRequest {
  title: string;
  description: string;
  erp_module: ERPModule;
  environment: Environment;
  business_unit: string;
}

export interface IncidentResponse {
  id: string;
  title: string;
  description: string;
  erp_module: ERPModule;
  environment: Environment;
  business_unit: string;
  severity: Severity;
  category: Category;
  auto_summary: string | null;
  suggested_action: string | null;
  status: IncidentStatus;
  created_at: string;
  updated_at: string;
}

