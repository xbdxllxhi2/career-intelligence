import json
import logging
import textwrap

logger = logging.getLogger(__name__)

JOBS_FILE = "./input/jobs/jobs.json"

def _load_jobs(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def _format_job(job: dict) -> dict:
    return {
        "reference": job.get("checksum"),
        "posted_at": job.get("date_posted"),
        "expires_at": job.get("date_validthrough") , 
        "title": job.get("title", "N/A"),
        "company": job.get("organization", "N/A"),
        "locations": ", ".join(job.get("locations_derived", [])) or "N/A",
        "description": textwrap.fill(job.get("description_text","")[:200]+"...", width=100),
        "score": job.get("match_score", {})
    }

def get_all_jobs() -> list[dict]:
    logger.debug("Getting all jobs")
    jobs = _load_jobs(JOBS_FILE)
    return [_format_job(job) for job in jobs.values()]

def get_job_by_reference(reference):
    logger.debug("Getting job with reference %s", reference)
    jobs= _load_jobs(JOBS_FILE)
    return jobs.get(reference)



def get_n_higher_jobs_score(n: int = 5) -> list[dict]:
    logger.debug("Getting top %d jobs by score", n)
    jobs = get_all_jobs()
    sorted_jobs = sorted(jobs, key=lambda j: j["score"], reverse=True)
    return sorted_jobs[:n]

def get_n_lowest_scores_jobs(n: int = 5) -> list[dict]:
    logger.debug("Getting bottom %d jobs by score", n)
    jobs = get_all_jobs()
    sorted_jobs = sorted(jobs, key=lambda j: j["score"])
    return sorted_jobs[:n]

