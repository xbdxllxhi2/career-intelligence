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
    remote BOOLEAN DEFAULT FALSE,

    details JSONB NOT NULL,

    organization_id INT REFERENCES organizations(organization_id) ON DELETE SET NULL,

    job_checksum CHAR(32) NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_jobs_checksum ON jobs(job_checksum);


CREATE TABLE jobs_history (
    history_id SERIAL PRIMARY KEY,
    job_id INT NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,

    old_details JSONB NOT NULL,
    old_checksum CHAR(32) NOT NULL,
    changed_at TIMESTAMP NOT NULL DEFAULT NOW()
);


CREATE TABLE applications (
    application_id SERIAL PRIMARY KEY,
    job_id INT NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,

    applied_at TIMESTAMP NOT NULL DEFAULT NOW(),
    resume_version TEXT,
    cover_letter TEXT,
    notes TEXT,

    status TEXT NOT NULL DEFAULT 'pending'
    -- statuses: pending, email_sent, interview, rejected, ghosted, offer
);


CREATE TABLE email_responses (
    email_id SERIAL PRIMARY KEY,
    application_id INT NOT NULL REFERENCES applications(application_id) ON DELETE CASCADE,

    subject TEXT,
    body TEXT,
    raw_email JSONB,

    email_checksum CHAR(32) NOT NULL,

    received_at TIMESTAMP NOT NULL DEFAULT NOW()
);


CREATE UNIQUE INDEX idx_email_checksum ON email_responses(email_checksum);
