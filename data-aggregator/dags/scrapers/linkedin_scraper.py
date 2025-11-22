import requests
import hashlib
import json
import time
import os

API_URL = "https://linkedin-job-search-api.p.rapidapi.com/active-jb-7d"
LOCAL_FILE ="./jobs.json"


HEADERS = {
    "x-rapidapi-key": "176b158518msh94f0d360f35aa2ap12a53ejsn8a999caef578",
    "x-rapidapi-host": "linkedin-job-search-api.p.rapidapi.com"
}


def load_existing_jobs():
    if not os.path.exists(LOCAL_FILE):
        return {}

    with open(LOCAL_FILE, "r", encoding="utf-8") as f:
        try:
            jobs_dict = json.load(f)
        except json.JSONDecodeError:
            return {}

    return jobs_dict 

def compute_checksum(item: dict) -> str:
    canonical = json.dumps(item, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def filter_new_jobs(jobs, file_path=LOCAL_FILE):
    existing = load_existing_jobs(file_path)
    existing_checksums = set(existing.keys())
    return {job["checksum"]: job for job in jobs if job["checksum"] not in existing_checksums}


def safe_request(url, headers, params, retries=5):
    # Make a request with retry logic and handle rate limits
    for attempt in range(retries):
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response
        if response.status_code == 429:
            wait = (attempt + 1) * 2
            print(f"Rate limit hit. Waiting {wait} seconds...")
            time.sleep(wait)
            continue
        if response.status_code == 403:
            print("API quota exceeded. Stopping.")
            return None
        response.raise_for_status()
    return None



def fetch_jobs(title_filter='"Stage Data Engineer"', location_filter='"France" OR "Nice, France"', max_jobs=1000, page_size=100):
    """
    Fetch jobs from the API with pagination.
    max_jobs: total number of jobs to fetch
    page_size: number of jobs per request (API limit)
    """
    jobs = []
    offset = 0

    while len(jobs) < max_jobs:
        params = {
            "limit": page_size,
            "offset": offset,
            "title_filter": title_filter,
            "location_filter": location_filter,
            "description_type": "text"
        }

        response = safe_request(API_URL, HEADERS, params)
        if response is None:
            break

        batch = response.json()
        if not batch:
            break

        for job in batch:
            job["checksum"] = compute_checksum(job)

        jobs.extend(batch)
        offset += page_size

        print(f"Fetched {len(jobs)} jobs so far...")
        
        if len(jobs) >= max_jobs:
            break

    return jobs[:max_jobs]



def save_jobs(jobs_dict):
    existing_jobs = load_existing_jobs()
    existing_jobs.update(jobs_dict)

    with open(LOCAL_FILE, "w", encoding="utf-8") as f:
        json.dump(existing_jobs, f, ensure_ascii=False, indent=2)
