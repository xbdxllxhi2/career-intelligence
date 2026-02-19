FROM apache/airflow:2.8.1-python3.11

USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy DAGs and plugins
COPY dags/ /opt/airflow/dags/
COPY plugins/ /opt/airflow/plugins/
