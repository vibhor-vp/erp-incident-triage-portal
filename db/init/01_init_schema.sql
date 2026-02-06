-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================
-- ENUMS
-- =====================
CREATE TYPE user_role AS ENUM ('ADMIN', 'USER');

CREATE TYPE erp_module AS ENUM (
  'AP', 'AR', 'GL', 'INVENTORY', 'HR', 'PAYROLL'
);

CREATE TYPE environment_type AS ENUM ('PROD', 'TEST');

CREATE TYPE incident_severity AS ENUM ('P1', 'P2', 'P3');

CREATE TYPE incident_category AS ENUM (
  'CONFIGURATION_ISSUE',
  'DATA_ISSUE',
  'INTEGRATION_FAILURE',
  'SECURITY_ACCESS',
  'UNKNOWN'
);

CREATE TYPE incident_status AS ENUM (
  'OPEN',
  'IN_PROGRESS',
  'RESOLVED',
  'CLOSED'
);

-- =====================
-- USERS
-- =====================
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  role user_role NOT NULL DEFAULT 'USER',
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =====================
-- INCIDENTS
-- =====================
CREATE TABLE incidents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  title TEXT NOT NULL,
  description TEXT NOT NULL,
  erp_module erp_module NOT NULL,
  environment environment_type NOT NULL,
  business_unit TEXT NOT NULL,

  severity incident_severity NOT NULL,
  category incident_category NOT NULL,
  auto_summary TEXT,
  suggested_action TEXT,

  status incident_status NOT NULL DEFAULT 'OPEN',

  created_by_id UUID REFERENCES users(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =====================
-- TRIGGERS
-- =====================
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_incidents_updated_at
BEFORE UPDATE ON incidents
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

-- =====================
-- SEED ADMIN USER
-- =====================
INSERT INTO users (name, email, role)
VALUES ('System Admin', 'admin@erp.local', 'ADMIN');
