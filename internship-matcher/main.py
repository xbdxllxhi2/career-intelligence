import logging
from sympy import true
import typer
from InquirerPy import inquirer


import json
from services.keyword_extractor import extract_keywords
from services.matcher import match_profile_sections
from services.llm_writer import generate_cv_section
from services.jobs_supplier import get_jobs
from services.profile_supplier import get_profile
from services.cv_factory import load_data
from services.orchestrator import create_cv



logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("internship-helper")

OUTPUT_DIR = "./output/cv"


def main():
    profile =  get_profile()
    jobs = get_jobs()
    for job_id, job in jobs.items():
        create_cv(job)

app = typer.Typer()

@app.command()
def choose():
    choice = inquirer.select(
        message="What do you want to do ?",
        choices=["See available jobs", "Evaluate cv", "Cherry"]
    ).execute()
    typer.echo(f"You picked {choice}")



if __name__ == "__main__":
    logger.info("Application started successfully")
    main()
