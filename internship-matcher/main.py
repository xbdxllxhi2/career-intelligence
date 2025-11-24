import typer
from InquirerPy import inquirer


import json
from services.keyword_extractor import extract_keywords
from services.matcher import match_profile_sections
from services.llm_writer import generate_cv_section
from services.jobs_supplier import get_jobs
from services.profile_supplier import get_profile
from services.cv_factory import generate_cv, load_data

OUTPUT_DIR = "./output/cv"

def main():
    profile =  get_profile()

    jobs = get_jobs()

    for job_id, job in jobs.items():
        description = job.get("description_text", "")
        keywords = extract_keywords(description)

        context = match_profile_sections(profile, keywords)
        print(f"Context got after matching {context}")

        cv_generated_text = generate_cv_section(context)
        print(f"Cv content {cv_generated_text}")

        cv_generated_text = cv_generated_text.replace("%", r"\%")
        cv_generated_text_safe = cv_generated_text.replace("\\", "\\\\")

        generated_cv_parts = json.loads(cv_generated_text_safe)

        static_cv_parts = load_data()
        complete_cv = {**static_cv_parts, **generated_cv_parts}

        print(f"complete cv: {complete_cv}")
        
        generate_cv(complete_cv)

        print(f"Generated: cv_{job_id}.txt")



app = typer.Typer()

@app.command()
def choose():
    choice = inquirer.select(
        message="What do you want to do ?",
        choices=["See available jobs", "Evaluate cv", "Cherry"]
    ).execute()
    typer.echo(f"You picked {choice}")

  

if __name__ == "__main__":
    # app()
    main()
