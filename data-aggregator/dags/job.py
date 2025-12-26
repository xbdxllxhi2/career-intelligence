from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from repositories.write_data_to_db_repo import export_to_postgres
from scrapers.linkedin_scraper import fetch_and_save



def export_to_sql(jobs_file_path="/opt/airflow/output/jobs/jobs.json"):
    export_to_postgres(jobs_file_path=jobs_file_path)


def scrape_and_save_jobs(title_filter='"Stage Data Engineer"'):
    return fetch_and_save(title_filter=title_filter)


def record_scores():
    # apply_scores()
    return "/opt/airflow/output/jobs/jobs.json"




TITLE_FITER = '''"Stage Data" 
OR "Stage Data Engineer"
OR "Stage Data Engineering"
OR "Stage DATA"
OR "Stage Data Analyst"
OR "Stage Data Science"
OR "Stage Big Data"
OR "Stage Machine Learning"
OR "Stage IA"
OR "Stage Intelligence Artificielle"
OR "Stage Business Intelligence"
OR "Stage ETL"
OR "Stage Data Platform"
OR "Stage Data Pipeline"
OR "Stage Cloud Data"
OR "Stage SQL"
OR "Stage Python Data"
OR "Stage Data Analytics"
OR "Stage Data Visualization"
OR "Stage Ingénierie logicielle"
OR "Full Stack Developer"
OR "Java"
OR "DevOps"
'''
# scrape >> transform >> export
with DAG(
    "job_pipelineV4",
    start_date=datetime(2025,12,26),
    schedule="@daily"
):
    scrape = PythonOperator(
        task_id="scrape",
        python_callable=scrape_and_save_jobs,
        op_kwargs={"title_filter": TITLE_FITER}
    )

    transform = PythonOperator(
        task_id="transform",
        python_callable=record_scores
    )

    export = PythonOperator(
        task_id="export",
        python_callable=export_to_sql,
        op_kwargs={"jobs_file_path": "/opt/airflow/output/jobs/jobs.json"}
    )

    scrape >> transform >> export
