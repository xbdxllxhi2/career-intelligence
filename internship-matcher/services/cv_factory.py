import json
import subprocess
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

INPUT_DIR ="./input"
TEMPLATE_DIR = F"{INPUT_DIR}/templates"
CONTEXT_DIR = f"{INPUT_DIR}/context"

OUTPUT_DIR = "./output/cv"
OUTPUT_TEX = f"{OUTPUT_DIR}/cv.tex"
OUTPUT_PDF = f"{OUTPUT_DIR}/cv.pdf"

def load_data():
    with open(f"{CONTEXT_DIR}/cv_data.json", "r", encoding="utf8") as f:
        return json.load(f)

def _render_template(context):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("cv_template.tex")
    rendered = template.render(context)

    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_TEX, "w", encoding="utf8") as f:
        f.write(rendered)

def _compile_pdf():
    subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", OUTPUT_TEX],
        cwd=OUTPUT_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def generate_cv(context):
    # context = _load_data()
    _render_template(context)
    _compile_pdf()
    print("CV generated → output/cv.pdf")



