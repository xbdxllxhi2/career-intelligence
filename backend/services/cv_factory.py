import json
import string
import subprocess
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import logging
from typing import Optional

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent
INPUT_DIR = BASE_DIR / "input"
TEMPLATE_DIR = INPUT_DIR / "templates"
CONTEXT_DIR = INPUT_DIR / "context"

OUTPUT_DIR = BASE_DIR / "output" / "cv"
OUTPUT_TEX = f"{OUTPUT_DIR}/cv.tex"
OUTPUT_PDF = f"{OUTPUT_DIR}/cv.pdf"


def _safe_path_component(value: str) -> str:
    # Avoid path traversal and OS path separator issues in generated output paths.
    return str(value).strip().replace("/", "_").replace("\\", "_")

def load_data():
    with open(f"{CONTEXT_DIR}/cv_data.json", "r", encoding="utf8") as f:
        return json.load(f)

def _render_template(tex_file_name, context, output_dir: Path):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("resume-template-2.tex")
    rendered = template.render(context)

    output_dir.mkdir(parents=True, exist_ok=True)

    with open(F"{output_dir}/{tex_file_name}.tex", "w", encoding="utf8") as f:
        f.write(rendered)

def _compile_pdf(tex_file_name:string, output_dir: Path):
    subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", tex_file_name],
        cwd=output_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def generate_cv(output_file_name, context, user_id: Optional[str] = None):
    logger.debug("complete cv context %s: ", json.dumps(context, indent=4))
    safe_output_file_name = _safe_path_component(output_file_name)

    if user_id:
        safe_user_id = _safe_path_component(user_id)
        output_dir = OUTPUT_DIR / safe_user_id
        relative_output_path = f"output/cv/{safe_user_id}/{safe_output_file_name}.pdf"
    else:
        raise ValueError("User ID is required to generate resume.")

    _render_template(safe_output_file_name, context, output_dir)
    _compile_pdf(safe_output_file_name, output_dir)
    print(f"CV generated to {relative_output_path}")
    return relative_output_path


