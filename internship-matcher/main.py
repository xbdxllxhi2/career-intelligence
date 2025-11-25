from email.policy import default
import logging
from random import choice
from regex import A
from sympy import im, true
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
from services.jobs_analyzer import analyze_jobs, perform_kmeans, build_company_skill_matrix

from repositories.jobs_repository import *
from repositories.pagination_helper import paginate_list


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
def generate_cv():
    user_input = inquirer.text(
    message="Enter the job reference you want to use:"
).execute()
    job_data = get_job_by_reference(user_input)

    if not job_data:
        typer.echo(f"No job found with reference: {user_input}")
        raise typer.Exit(code=1)
    create_cv(job_data)

@app.command()
def get_jobs():
    job_choices = {
        1:"See all jobs",
        2: "See 5 top jobs by score",
        3: "See lower 5 jobs by score"
    }

    choice = inquirer.select(
    message="Which jobs would you like to see boss ?",
    choices=[{"name": f"{k} - {v}", "value": k} for k, v in job_choices.items()],
    ).execute()

    match choice:
        case 1:
            paginate_list(get_all_jobs())
        case 2:
            pass
        case 3:
            pass
        case _:
            print("unkown option")


@app.command()
def analyze():
    action_choices = {
        1:"See my top wanted skills",
        2: "Analyze jobs data",
    }

    choice = inquirer.select(
    message="Which jobs would you like to see boss ?",
    choices=[{"name": f"{k} - {v}", "value": k} for k, v in action_choices.items()],
    ).execute()

    match choice:
        case 1:
            _get_my_top_wanted_skills()
        case 2:
            analyze_jobs()
        case _:
            print("unkown option")


def _get_my_top_wanted_skills():
    jobs = get_all_raw_jobs()
    profile = get_profile()
    all_skills = []
    for category, skills_list in profile.get("skills").items():
        all_skills.extend(skills_list)
 
    profile_skills = sorted(set(all_skills))
    build_company_skill_matrix(jobs, profile_skills)
    

if __name__ == "__main__":
    logger.info("Application started successfully")
    app()
