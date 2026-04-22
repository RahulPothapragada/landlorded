-- Profiles table — auto-created on first login
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    tenant_name TEXT DEFAULT '',
    landlord_name TEXT DEFAULT '',
    premises TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Enable RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own profile"
    ON profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON profiles FOR UPDATE
    USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile"
    ON profiles FOR INSERT
    WITH CHECK (auth.uid() = id);


-- Audits table
CREATE TABLE IF NOT EXISTS audits (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'processing' CHECK (status IN ('processing', 'complete', 'failed')),
    mode TEXT NOT NULL DEFAULT 'audit' CHECK (mode IN ('audit', 'dispute', 'renewal')),
    file_name TEXT DEFAULT '',
    page_count INTEGER,
    ocr_used BOOLEAN DEFAULT FALSE,
    risk_level TEXT CHECK (risk_level IN ('HIGH', 'MODERATE', 'LOW')),
    red_flags INTEGER DEFAULT 0,
    yellow_flags INTEGER DEFAULT 0,
    patterns JSONB DEFAULT '[]'::jsonb,
    documents_available TEXT[] DEFAULT '{}',
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_audits_user_id ON audits(user_id);
CREATE INDEX idx_audits_created_at ON audits(created_at DESC);

-- Enable RLS
ALTER TABLE audits ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own audits"
    ON audits FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own audits"
    ON audits FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own audits"
    ON audits FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own audits"
    ON audits FOR DELETE
    USING (auth.uid() = user_id);


-- Storage bucket (run this in Supabase dashboard or via API)
-- INSERT INTO storage.buckets (id, name, public) VALUES ('landlorded', 'landlorded', false);

-- Storage RLS policies
-- Users can only access files in their own folder (user_id prefix)
