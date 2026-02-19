-- Create databases
CREATE DATABASE airflow_db;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE internships_db TO internships;
GRANT ALL PRIVILEGES ON DATABASE airflow_db TO internships;

-- Connect to internships_db and create extensions
\c internships_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Connect to airflow_db
\c airflow_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
