import json
import logging
import subprocess
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "input"
TEMPLATE_DIR = INPUT_DIR / "templates"
CONTEXT_DIR = INPUT_DIR / "context"
OUTPUT_DIR = BASE_DIR / "output" / "cv"


def load_data():
    with open(CONTEXT_DIR / "cv_data.json", "r", encoding="utf8") as f:
        return json.load(f)


def _render_template(tex_file_name, context):
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template("resume-template-2.tex")
    rendered = template.render(context)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    tex_path = OUTPUT_DIR / f"{tex_file_name}.tex"
    with open(tex_path, "w", encoding="utf8") as f:
        f.write(rendered)

    return tex_path


def _compile_pdf(tex_path: Path):
    result = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", tex_path.name],
        cwd=str(OUTPUT_DIR),
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"pdflatex failed with code {result.returncode}\n"
            f"stdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"
        )


def generate_cv(output_file_name, context):
    logger.debug("complete cv context: %s", json.dumps(context, indent=4))

    tex_path = _render_template(output_file_name, context)
    _compile_pdf(tex_path)

    pdf_path = OUTPUT_DIR / f"{output_file_name}.pdf"

    if not pdf_path.exists():
        raise FileNotFoundError(f"Expected PDF was not created: {pdf_path}")

    logger.info("CV generated to %s", pdf_path)
    return str(pdf_path)