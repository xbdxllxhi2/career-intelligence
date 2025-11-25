import spacy
import logging

logger = logging.getLogger(__name__)

nlp = spacy.load("fr_core_news_sm")

STOPWORDS =nlp.Defaults.stop_words

def extract_keywords(text: str):
    doc = nlp(text.lower())
    tokens = [
        token.lemma_
        for token in doc
        if token.pos_ in {"NOUN", "PROPN", "VERB"} and token.text not in STOPWORDS
    ]
    return sorted(set(tokens))

def extract_job_skills(text: str, known_skills: list[str]):
    if not text:
        return []

    keywords = extract_keywords(text)
    found = [skill for skill in known_skills if skill.lower() in keywords]
    
    extracted_job_skills = set(found)
    logger.debug("Extarcted job skills %s", extracted_job_skills)
    
    return extracted_job_skills



def get_job_required_skills(raw_jobs: list[dict],skills_criteria: list[str]):
    result = {}

    for job in raw_jobs:
        reference = job.get("checksum", "unknown_ref")
        title = job.get("title", "No Title")
        company = job.get("organization", "-")
        description = job.get("description_text", "") 

        keywords = extract_keywords(description)
        skills = extract_job_skills(description, skills_criteria)

        result[reference] = {
            "title": title,
            "company": company,
            "skills": skills,
            "keywords": keywords,
        }

    return result
