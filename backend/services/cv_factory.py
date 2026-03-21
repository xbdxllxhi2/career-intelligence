import json
import string
import subprocess
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent
INPUT_DIR = BASE_DIR / "input"
TEMPLATE_DIR = INPUT_DIR / "templates"
CONTEXT_DIR = INPUT_DIR / "context"

OUTPUT_DIR = BASE_DIR / "output" / "cv"
OUTPUT_TEX = f"{OUTPUT_DIR}/cv.tex"
OUTPUT_PDF = f"{OUTPUT_DIR}/cv.pdf"

def load_data():
    with open(f"{CONTEXT_DIR}/cv_data.json", "r", encoding="utf8") as f:
        return json.load(f)

def _render_template(tex_file_name,context):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("resume-template-2.tex")
    rendered = template.render(context)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(F"{OUTPUT_DIR}/{tex_file_name}.tex", "w", encoding="utf8") as f:
        f.write(rendered)

def _compile_pdf(tex_file_name:string):
    subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", tex_file_name],
        cwd=OUTPUT_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def generate_cv(output_file_name, context):
    logger.debug("complete cv context %s: ", json.dumps(context, indent=4))
    _render_template(output_file_name, context)
    _compile_pdf(output_file_name)
    print(f"CV generated to output/cv/{output_file_name}.pdf")
    return f"output/cv/{output_file_name}.pdf"


