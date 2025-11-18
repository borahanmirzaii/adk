-- Initial database schema for ADK Dev Environment Manager

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";

-- Sessions table for ADK session management
CREATE TABLE IF NOT EXISTS adk_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT UNIQUE NOT NULL,
    user_id TEXT NOT NULL,
    app_name TEXT NOT NULL DEFAULT 'adk-devops-assistant',
    state JSONB DEFAULT '{}',
    events JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_adk_sessions_user_id ON adk_sessions(user_id);
CREATE INDEX idx_adk_sessions_session_id ON adk_sessions(session_id);
CREATE INDEX idx_adk_sessions_updated_at ON adk_sessions(updated_at);

-- Session history for tracking agent interactions
CREATE TABLE IF NOT EXISTS session_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT NOT NULL REFERENCES adk_sessions(session_id) ON DELETE CASCADE,
    user_message TEXT NOT NULL,
    agent_response TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_session_history_session_id ON session_history(session_id);
CREATE INDEX idx_session_history_agent_name ON session_history(agent_name);
CREATE INDEX idx_session_history_created_at ON session_history(created_at);

-- Infrastructure metrics table
CREATE TABLE IF NOT EXISTS infrastructure_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_name TEXT NOT NULL,
    metric_type TEXT NOT NULL,
    metric_value NUMERIC NOT NULL,
    unit TEXT,
    status TEXT NOT NULL CHECK (status IN ('healthy', 'warning', 'critical')),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_infrastructure_metrics_service_name ON infrastructure_metrics(service_name);
CREATE INDEX idx_infrastructure_metrics_status ON infrastructure_metrics(status);
CREATE INDEX idx_infrastructure_metrics_created_at ON infrastructure_metrics(created_at);

-- Code reviews table
CREATE TABLE IF NOT EXISTS code_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_id TEXT UNIQUE NOT NULL,
    code_hash TEXT NOT NULL,
    file_path TEXT,
    review_type TEXT NOT NULL CHECK (review_type IN ('static_analysis', 'security', 'best_practices', 'full')),
    review_result JSONB NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'in_progress', 'completed', 'failed')),
    workflow_state JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_code_reviews_review_id ON code_reviews(review_id);
CREATE INDEX idx_code_reviews_code_hash ON code_reviews(code_hash);
CREATE INDEX idx_code_reviews_status ON code_reviews(status);

-- Deployments table
CREATE TABLE IF NOT EXISTS deployments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deployment_id TEXT UNIQUE NOT NULL,
    service_name TEXT NOT NULL,
    version TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'in_progress', 'success', 'failed', 'rolled_back')),
    workflow_state JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_deployments_deployment_id ON deployments(deployment_id);
CREATE INDEX idx_deployments_service_name ON deployments(service_name);
CREATE INDEX idx_deployments_status ON deployments(status);

-- Knowledge base documents table (for RAG)
CREATE TABLE IF NOT EXISTS knowledge_base_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    content_type TEXT NOT NULL CHECK (content_type IN ('code', 'documentation', 'decision', 'note')),
    file_path TEXT,
    embedding vector(1536), -- OpenAI compatible embedding size
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_knowledge_base_documents_document_id ON knowledge_base_documents(document_id);
CREATE INDEX idx_knowledge_base_documents_content_type ON knowledge_base_documents(content_type);
CREATE INDEX idx_knowledge_base_documents_embedding ON knowledge_base_documents USING ivfflat (embedding vector_cosine_ops);

-- Agent status table for real-time monitoring
CREATE TABLE IF NOT EXISTS agent_status (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('running', 'idle', 'error', 'stopped')),
    last_heartbeat TIMESTAMPTZ DEFAULT NOW(),
    metrics JSONB DEFAULT '{}',
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(agent_name)
);

CREATE INDEX idx_agent_status_agent_name ON agent_status(agent_name);
CREATE INDEX idx_agent_status_status ON agent_status(status);
CREATE INDEX idx_agent_status_last_heartbeat ON agent_status(last_heartbeat);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_adk_sessions_updated_at BEFORE UPDATE ON adk_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_base_documents_updated_at BEFORE UPDATE ON knowledge_base_documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agent_status_updated_at BEFORE UPDATE ON agent_status
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE adk_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE session_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE infrastructure_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE code_reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE deployments ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_base_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_status ENABLE ROW LEVEL SECURITY;

-- RLS Policies (allow all for now - customize based on auth requirements)
CREATE POLICY "Allow all operations" ON adk_sessions FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON session_history FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON infrastructure_metrics FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON code_reviews FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON deployments FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON knowledge_base_documents FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON agent_status FOR ALL USING (true);

