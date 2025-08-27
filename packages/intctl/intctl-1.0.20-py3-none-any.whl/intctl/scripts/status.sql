CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS service_status (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_name TEXT NOT NULL,
    action TEXT NOT NULL,
    status TEXT NOT NULL,
    source TEXT,
    resource_id TEXT,
    project_id UUID,
    project_name TEXT,
    workspace_id UUID NOT NULL,
    message TEXT,
    execution_id TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS api_keys (
    key_id TEXT PRIMARY KEY,
    project_uuid TEXT NOT NULL,
    projectname TEXT NOT NULL,
    username TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    revoked BOOLEAN DEFAULT FALSE,
    deleted BOOLEAN DEFAULT FALSE,
    modified_by TEXT,
    modified_at TIMESTAMP WITH TIME ZONE
);