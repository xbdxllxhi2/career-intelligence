from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

from scripts.scraper import scrape_jobs
from scripts.data_cleaner import clean_data
from scripts.saver import save_as_excel

with DAG(
    "job_pipeline",
    start_date=datetime(2025,11,22),
    schedule="@daily"
):
    scrape = PythonOperator(
        task_id="scrape",
        python_callable=scrape_jobs
    )

    transform = PythonOperator(
        task_id="transform",
        python_callable=clean_data
    )

    export = PythonOperator(
        task_id="export",
        python_callable=save_as_excel
    )

    scrape >> transform >> export
