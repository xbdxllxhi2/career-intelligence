-- Create read-only AI user
CREATE USER ai_readonly WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE jobsdb TO ai_readonly;
GRANT USAGE ON SCHEMA public TO ai_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO ai_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO ai_readonly;


CREATE TABLE if NOT EXISTS organizations (
    organization_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    website TEXT,
    logo_url TEXT,
    industry TEXT,
    size_bucket TEXT,
    employees INT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_org_name UNIQUE (name)
);

CREATE TABLE if NOT EXISTS sources (
    source_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    domain TEXT,
    source_type TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_source UNIQUE (name, domain)
);


CREATE TABLE if NOT EXISTS locations (
    location_id SERIAL PRIMARY KEY,
    country TEXT,
    region TEXT,
    city TEXT,
    lat DOUBLE PRECISION,
    lng DOUBLE PRECISION,
    timezone TEXT
);


CREATE TABLE if NOT EXISTS jobs (
    job_id SERIAL PRIMARY KEY,

    title TEXT NOT NULL,
    description TEXT,

    job_url TEXT,
    external_id TEXT,

    seniority TEXT,
    employment_type TEXT[],
    remote BOOLEAN,

    posted_at TIMESTAMP,
    expires_at TIMESTAMP,

    source_id INT NOT NULL REFERENCES sources(source_id),
    organization_id INT REFERENCES organizations(organization_id),
    location_id INT REFERENCES locations(location_id),
    has_easy_apply BOOLEAN,
    job_checksum CHAR(64) NOT NULL,
    raw JSONB NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_job_checksum UNIQUE (job_checksum)
);


CREATE INDEX idx_jobs_source ON jobs(source_id);
CREATE INDEX idx_jobs_org ON jobs(organization_id);
CREATE INDEX idx_jobs_location ON jobs(location_id);
CREATE INDEX idx_jobs_expires ON jobs(expires_at);




