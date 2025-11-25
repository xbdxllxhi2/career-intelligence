import json
import string
import subprocess
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

INPUT_DIR ="./input"
TEMPLATE_DIR = F"{INPUT_DIR}/templates"
CONTEXT_DIR = f"{INPUT_DIR}/context"

OUTPUT_DIR = "./output/cv"
OUTPUT_TEX = f"{OUTPUT_DIR}/cv.tex"
OUTPUT_PDF = f"{OUTPUT_DIR}/cv.pdf"

def load_data():
    with open(f"{CONTEXT_DIR}/cv_data.json", "r", encoding="utf8") as f:
        return json.load(f)

def _render_template(tex_file_name,context):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("cv_template.tex")
    rendered = template.render(context)

    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    with open(F"{OUTPUT_DIR}/{tex_file_name}.tex", "w", encoding="utf8") as f:
        f.write(rendered)

def _compile_pdf(tex_file_name:string):
    subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", tex_file_name],
        cwd=OUTPUT_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def generate_cv(job, context):
    logger.debug("complete cv context %s: ", json.dumps(context, indent=4))
    output_file_name = job['id']

    _render_template(output_file_name, context)
    _compile_pdf(output_file_name)
    logger.info("CV generated to output/cv.pdf")


