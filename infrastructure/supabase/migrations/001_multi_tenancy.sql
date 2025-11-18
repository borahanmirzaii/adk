-- Multi-tenancy support with Row Level Security (RLS)

-- Create tenants table
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add tenant_id to sessions table
ALTER TABLE sessions 
ADD COLUMN IF NOT EXISTS tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE;

-- Add tenant_id to agent_status table
ALTER TABLE agent_status 
ADD COLUMN IF NOT EXISTS tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE;

-- Create index for tenant_id lookups
CREATE INDEX IF NOT EXISTS idx_sessions_tenant_id ON sessions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_agent_status_tenant_id ON agent_status(tenant_id);

-- Enable Row Level Security
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_status ENABLE ROW LEVEL SECURITY;

-- RLS Policies for sessions
CREATE POLICY "Users can only see their own tenant's sessions"
    ON sessions
    FOR SELECT
    USING (
        tenant_id IN (
            SELECT tenant_id 
            FROM auth.users 
            WHERE id = auth.uid()
        )
    );

CREATE POLICY "Users can only create sessions for their tenant"
    ON sessions
    FOR INSERT
    WITH CHECK (
        tenant_id IN (
            SELECT tenant_id 
            FROM auth.users 
            WHERE id = auth.uid()
        )
    );

CREATE POLICY "Users can only update their own tenant's sessions"
    ON sessions
    FOR UPDATE
    USING (
        tenant_id IN (
            SELECT tenant_id 
            FROM auth.users 
            WHERE id = auth.uid()
        )
    );

-- RLS Policies for agent_status
CREATE POLICY "Users can only see their own tenant's agent status"
    ON agent_status
    FOR SELECT
    USING (
        tenant_id IN (
            SELECT tenant_id 
            FROM auth.users 
            WHERE id = auth.uid()
        )
    );

CREATE POLICY "Users can only create agent status for their tenant"
    ON agent_status
    FOR INSERT
    WITH CHECK (
        tenant_id IN (
            SELECT tenant_id 
            FROM auth.users 
            WHERE id = auth.uid()
        )
    );

-- Function to get current user's tenant_id
CREATE OR REPLACE FUNCTION get_user_tenant_id()
RETURNS UUID AS $$
    SELECT (raw_user_meta_data->>'tenant_id')::UUID
    FROM auth.users
    WHERE id = auth.uid();
$$ LANGUAGE sql SECURITY DEFINER;

-- Create default tenant for existing data
INSERT INTO tenants (id, name, slug) 
VALUES ('00000000-0000-0000-0000-000000000000', 'Default Tenant', 'default')
ON CONFLICT (slug) DO NOTHING;

-- Update existing sessions to use default tenant
UPDATE sessions 
SET tenant_id = '00000000-0000-0000-0000-000000000000'
WHERE tenant_id IS NULL;

-- Update existing agent_status to use default tenant
UPDATE agent_status 
SET tenant_id = '00000000-0000-0000-0000-000000000000'
WHERE tenant_id IS NULL;

