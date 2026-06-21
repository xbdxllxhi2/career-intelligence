"""Prompts for the LangGraph resume generation agent.

The generation prompt embeds real, high-quality resumes (stored under
``input/reference_resumes``) as few-shot style references so the agent mimics
their tone, density and bullet style.
"""

import logging
from functools import lru_cache
from pathlib import Path

logger = logging.getLogger(__name__)

REFERENCE_DIR = Path(__file__).parent.parent / "input" / "reference_resumes"

# pdftotext leaves a few replacement artifacts; tidy the worst of them so the
# few-shot examples read cleanly.
_CLEANUP = {
    "�": "e",  # replacement char most often stands in for an accented e
    "•": "-",
    "\f": "\n",
}


def _clean(text: str) -> str:
    for bad, good in _CLEANUP.items():
        text = text.replace(bad, good)
    return text.strip()


@lru_cache(maxsize=1)
def load_reference_examples() -> str:
    """Load and concatenate the reference resumes used as few-shot examples."""
    if not REFERENCE_DIR.exists():
        logger.warning("Reference resumes directory not found: %s", REFERENCE_DIR)
        return ""

    blocks: list[str] = []
    for path in sorted(REFERENCE_DIR.glob("*.txt")):
        try:
            raw = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:  # pragma: no cover - defensive
            logger.warning("Could not read reference resume %s: %s", path, exc)
            continue
        blocks.append(f"--- REFERENCE RESUME: {path.stem} ---\n{_clean(raw)}")

    return "\n\n".join(blocks)


# Shared, language-agnostic structural contract describing the JSON schema the
# agent must fill. Kept separate so EN and FR prompts stay in sync.
_SCHEMA_CONTRACT = """
You produce ONLY the structured object with these exact fields:
- "language": "en" or "fr" (must match the language you are writing in).
- "objective": a single dense sentence (28-42 words) positioning the candidate's
  level, core expertise, the value delivered, and the target role/internship.
  No "I", no listed technologies, no empty superlatives ("passionate", "expert").
- "skills": a list of 3 to 5 categories. Each category has a short "category"
  label (2-4 words, e.g. "Programming & Data", "Machine Learning & GenAI",
  "MLOps & DevOps", "Databases") and an "items" list of 4-9 keyword skills
  (1-3 words each). No duplicates across categories. Prioritise keywords from
  the job offer, then transferable strengths from the profile.
- "experience": 1 to 3 entries, most recent first. Each has "title", "company",
  "start_date", "end_date" (or null / "Present" if ongoing), "location",
  "context" (one short italic line on the company/mission scope), and "bullets".
  Use 2-4 bullets per entry, 90-150 characters each, starting with a strong
  action verb, combining action + method/technology + measurable impact.
- "projects": 0 to 3 entries. Each has "title", optional "subtitle" (tech-stack
  tagline), optional "url", optional "year", and "bullets" (1-3 bullets,
  impact-oriented, technology made explicit).
"""

_RULES = """
Hard rules:
- NEVER invent facts, technologies, employers, dates or metrics. Use ONLY what
  the profile provides. When a metric is not available, write a credible
  qualitative impact instead of a fabricated number.
- Tailor ordering and vocabulary to the job offer while preserving transferable
  strengths from the profile.
- The whole resume MUST fit on ONE A4 page. Be selective: pick the most relevant
  experiences and projects rather than listing everything. Density over breadth.
- No emojis, no fancy quotes, no line breaks inside a bullet, no pronouns.
"""


def get_generation_prompt(language: str) -> str:
    """System prompt for the initial generation step."""
    examples = load_reference_examples()
    examples_section = (
        f"\nStudy these real, high-quality resumes. Match their tone, density and "
        f"bullet style (NOT their facts):\n\n{examples}\n"
        if examples
        else ""
    )

    if language == "fr":
        intro = (
            "Tu es un expert senior en rédaction de CV ATS pour profils data et "
            "ingénierie logicielle, agissant comme recruteur exigeant. Tu rédiges "
            "en FRANÇAIS un CV ciblé, crédible, dense et professionnel, tenant sur "
            "UNE seule page A4."
        )
    else:
        intro = (
            "You are a senior ATS resume writer for data and software engineering "
            "profiles, acting as a demanding hiring manager. You write in ENGLISH a "
            "targeted, credible, dense and professional resume that fits on ONE A4 page."
        )

    return f"{intro}\n{_SCHEMA_CONTRACT}\n{_RULES}\n{examples_section}"


def get_condense_prompt(language: str, overflow_pages: int) -> str:
    """System prompt for the condensing step when the PDF overflows one page."""
    if language == "fr":
        return f"""Tu es un expert en optimisation de CV. Le CV généré occupe
{overflow_pages} pages mais DOIT tenir sur UNE SEULE page A4.

Condense le contenu fourni SANS rien inventer ni supprimer d'information critique :
- Raccourcis les bullets (vise 90-120 caractères) et fusionne les redondances.
- Réduis le nombre de bullets par expérience/projet, puis le nombre de projets,
  puis d'expériences, en gardant les plus pertinents pour l'offre.
- Garde 3 à 4 catégories de compétences maximum, items resserrés.
- Conserve exactement le même schéma de sortie structuré.
{_RULES}"""

    return f"""You are a resume optimization expert. The generated resume spans
{overflow_pages} pages but MUST fit on ONE A4 page.

Condense the provided content WITHOUT inventing anything or dropping critical
information:
- Shorten bullets (aim for 90-120 characters) and merge redundant points.
- Reduce the number of bullets per entry, then the number of projects, then
  experiences, keeping the most relevant to the offer.
- Keep at most 3-4 skill categories with tightened item lists.
- Keep the exact same structured output schema.
{_RULES}"""
