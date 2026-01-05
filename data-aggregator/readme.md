# Career Intelligence Data Aggregator

**Career Intelligence Data Aggregator** is a Python-based platform designed to collect, normalize, and store job and internship postings efficiently. The system ensures data integrity, prevents duplicates, and stores information in a structured PostgreSQL database for easy access and further processing.  

## Key Features

- **Customizable Job Fetching:** Retrieve job postings using filters such as title, location, and description type.  
- **Data Normalization:** Standardizes the structure of job postings for consistency across datasets.  
- **Duplicate Prevention:** Detects duplicates using SHA256 checksums to maintain clean storage.  
- **Persistent Storage:** Stores all job postings in a PostgreSQL database for reliable access and management.  
- **Tested and Reliable:** Includes unit tests to ensure correct fetching, normalization, and storage logic.  

## Use Cases

- Centralize job postings for personal or organizational dashboards.  
- Maintain a clean, normalized dataset for career intelligence projects.  
- Serve as a foundation for downstream applications such as search engines or reporting tools.  

## Getting Started

This project uses **Docker Compose** to manage its services, including the PostgreSQL database and Airflow for job orchestration. A `Makefile` is provided to simplify common tasks.

### Prerequisites

- [Docker](https://www.docker.com/) installed  
- [Docker Compose](https://docs.docker.com/compose/) installed  
- Git (to clone the repository)  

### Clone the repository:

```bash
git clone <your-repo-url>
cd <repository-folder>
```

## Initialize the Airflow database

```
make init
```

## Create an admin user for Airflow

```
make user
```

## Install Python dependencies inside the Airflow containers

```
make install-requirements
```

## Running the Platform

### Start all services in the background

```
make start
```

### Stop all services

```
make stop
```

### Restart the services

```
make restart
```

### View logs

```
make logs
```

### Reset the environment (clears volumes, logs, and cache)

```
make reset
```

## Notes

- The job fetcher and storage logic is executed as part of the Airflow DAGs.  
- PostgreSQL stores all normalized job postings for easy access and further processing.  
- You can access the Airflow web interface at `http://localhost:8080` (default credentials: `admin` / `admin`).

