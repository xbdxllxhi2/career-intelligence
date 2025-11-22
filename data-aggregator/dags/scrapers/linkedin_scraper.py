from datetime import datetime
import requests
import hashlib
import json
import time
import os

API_URL = "https://linkedin-job-search-api.p.rapidapi.com/active-jb-7d"
LOCAL_FILE ="/opt/airflow/dags/data/jobs.json"


HEADERS = {
    "x-rapidapi-key": "ca5661ba8cmshf11ead7efed175dp163c0ejsn6b93942c77c6",
    "x-rapidapi-host": "linkedin-job-search-api.p.rapidapi.com"
}


def load_existing_jobs(file_path=LOCAL_FILE):
    if not os.path.exists(file_path):
        return {}

    with open(file_path, "r", encoding="utf-8") as f:
        try:
            jobs_dict = json.load(f)
        except json.JSONDecodeError:
            return {}

    return jobs_dict 

def compute_checksum(item: dict) -> str:
    canonical = json.dumps(item, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def filter_new_jobs(jobs:list, file_path=LOCAL_FILE):
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

        now = datetime.utcnow().isoformat() + "Z"
        for job in batch:
            job["checksum"] = compute_checksum(job)
            job["fetched_at"] = now

        jobs.extend(batch)
        offset += page_size

        print(f"Fetched {len(jobs)} jobs so far...")
        
        if len(jobs) >= max_jobs:
            break

    return jobs



def save_jobs(jobs_dict:dict):
    existing_jobs = load_existing_jobs()
    existing_jobs.update(jobs_dict)

    with open(LOCAL_FILE, "w", encoding="utf-8") as f:
        json.dump(existing_jobs, f, ensure_ascii=False, indent=2)


def fetch_and_save(title_filter ='"Stage Data Engineer"' ,max_jobs=1000, page_size=100):
    jobs_list = fetch_jobs(title_filter=title_filter, max_jobs=max_jobs, page_size=page_size)

    new_jobs = filter_new_jobs(jobs_list)
    
    if not new_jobs:
        print("No new jobs to save.")
        return
    # jobs_dict = {job["checksum"]: job for job in jobs_list}

    save_jobs(new_jobs)
    print(f"Saved {len(new_jobs)} new jobs to {LOCAL_FILE}.")
