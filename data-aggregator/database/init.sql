-- Create read-only AI user
CREATE USER ai_readonly WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE jobsdb TO ai_readonly;
GRANT USAGE ON SCHEMA public TO ai_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO ai_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO ai_readonly;


CREATE TABLE if NOT EXISTS organizations (
    organization_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,

    logo_url TEXT,
    industry TEXT,
    slogan TEXT,

    size_bucket TEXT,
    website TEXT,
    description text,

    org_type TEXT,

    employees INT,
    followers INT,

    founded_date TIMESTAMP,

    CONSTRAINT uq_org_name UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS specialities (
    speciality_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,

    CONSTRAINT uq_speciality_name UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS organization_specialities (
    organization_id INT NOT NULL,
    speciality_id   INT NOT NULL,

    PRIMARY KEY (organization_id, speciality_id),

    CONSTRAINT fk_org_specialities_org
        FOREIGN KEY (organization_id)
        REFERENCES organizations (organization_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_org_specialities_speciality
        FOREIGN KEY (speciality_id)
        REFERENCES specialities (speciality_id)
        ON DELETE CASCADE
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
    source_apply_url TEXT,
    external_id TEXT,

    seniority TEXT,
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

CREATE TABLE employment_types (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE job_employment_types (
    job_id INT,
    employment_type_id INT,
    PRIMARY KEY (job_id, employment_type_id),

    CONSTRAINT fk_job_employment_types_job
        FOREIGN KEY (job_id)
        REFERENCES jobs(job_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_job_employment_types_emp_type
        FOREIGN KEY (employment_type_id)
        REFERENCES  employment_types(id)
        ON DELETE CASCADE
);


CREATE INDEX idx_organizations_industry ON organizations(industry);
CREATE INDEX idx_organizations_org_type ON organizations(org_type);

CREATE INDEX idx_org_specialities_org ON organization_specialities(organization_id);
CREATE INDEX idx_org_specialities_speciality ON organization_specialities(speciality_id);

CREATE INDEX idx_jobs_source ON jobs(source_id);
CREATE INDEX idx_jobs_org ON jobs(organization_id);
CREATE INDEX idx_jobs_location ON jobs(location_id);

CREATE INDEX idx_job_emp_types_job ON job_employment_types(job_id);
CREATE INDEX idx_job_emp_types_type ON job_employment_types(employment_type_id);





