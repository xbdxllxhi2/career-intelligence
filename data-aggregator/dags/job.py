from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

from scripts.scraper import scrape_and_save_jobs
from scripts.data_cleaner import clean_data
from scripts.saver import save_as_excel


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
'''

with DAG(
    "job_pipeline",
    start_date=datetime(2025,11,22),
    schedule="@daily"
):
    scrape = PythonOperator(
        task_id="scrape",
        python_callable=scrape_and_save_jobs,
        op_kwargs={"title_filter": TITLE_FITER}
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
