import json
from typing import Any
from models.local_schemaV1 import JobSchema

def get_jobs_dict(file) -> dict[dict[str, Any]]:
    with open(file, "r") as f:
        job_offers = json.load(f)

    return job_offers