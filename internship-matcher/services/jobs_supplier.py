import json

JOBS_FILE = "./input/jobs/jobs.json"

def get_jobs()->dict:
    with open(JOBS_FILE) as f:
        jobs = json.load(f)
    return jobs