CREATE TABLE organizations (
    organization_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    logo_url TEXT,
    website TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE jobs (
    job_id SERIAL PRIMARY KEY,
    job_title TEXT NOT NULL,
    job_url TEXT UNIQUE,
    source TEXT NOT NULL,
    location TEXT,
    description TEXT,
    remote BOOLEAN DEFAULT FALSE,
    raw JSONB NOT NULL,
    organization_id INT REFERENCES organizations(organization_id) ON DELETE SET NULL,
    job_checksum CHAR(64) NOT NULL,
    expires_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_jobs_checksum ON jobs(job_checksum);

CREATE TABLE job_score (
    id SERIAL PRIMARY KEY,
    job_id INT NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    metric TEXT NOT NULL,
    factor TEXT,
    value FLOAT NOT NULL,
    description TEXT
);

CREATE TABLE applications (
    application_id SERIAL PRIMARY KEY,
    job_id INT NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    applied_at TIMESTAMP NOT NULL DEFAULT NOW(),
    resume_version TEXT,
    cover_letter TEXT,
    notes TEXT,
    status TEXT NOT NULL DEFAULT 'pending'
);

CREATE TABLE email_responses (
    email_id SERIAL PRIMARY KEY,
    application_id INT NOT NULL REFERENCES applications(application_id) ON DELETE CASCADE,
    subject TEXT,
    body TEXT,
    raw_email JSONB,
    received_at TIMESTAMP NOT NULL DEFAULT NOW()
);
