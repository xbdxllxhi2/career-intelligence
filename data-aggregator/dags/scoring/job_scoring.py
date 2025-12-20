import math
import json
# import fasttext
import numpy as np

CV_FILE_PATH = "/opt/airflow/input/context/cv_data.json"
JOBS_FILE_PATH = "/opt/airflow/output/jobs/jobs.json"

# FASTTEXT_MODEL = fasttext.load_model("/opt/airflow/input/models/cc.fr.300.bin")


# Load CV and job offer files
def load_json_files():
    with open(CV_FILE_PATH, "r") as f:
        cv_data = json.load(f)

    with open(JOBS_FILE_PATH, "r") as f:
        job_offers = json.load(f)

    return cv_data, job_offers


cv_data, job_offers = load_json_files()


# Scoring functions
def fasttext_embed(text: str):
    pass
    # return FASTTEXT_MODEL.get_sentence_vector(text)


def fasttext_similarity(text1: str, text2: str):
    v1 = fasttext_embed(text1)
    v2 = fasttext_embed(text2)

    # Cosine similarity
    return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))


def keyword_score(cv_skills, job_skills):
    all_cv_skills = (
        cv_skills["technical"] +
        cv_skills["tools"] +
        cv_skills["soft"]
    )

    matched = set(all_cv_skills).intersection(set(job_skills))
    return len(matched) / max(len(job_skills), 1)


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in km
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c  

def location_score(job):
    if not job.get("locations_raw"):
        return 0.5

    job_loc = job["locations_raw"][0]
    job_lat = job_loc.get("latitude")
    job_long = job_loc.get("longitude")

    my_lat, my_long = 43.569904, 7.112179

    dist_km = haversine_distance(my_lat, my_long, job_lat, job_long)

    if dist_km < 10:
        return 1.0
    elif dist_km < 50:
        return 0.8
    elif dist_km < 100:
        return 0.5
    else:
        return 0.2



# Compute score for ONE job offer
def compute_total_score(cv_data, job_offer):
    kw_score = keyword_score(
        cv_data["skills"],
        job_offer["required_skills"]
    )

    cv_text = " ".join(
        cv_data["skills"]["technical"] +
        cv_data["skills"]["soft"] +
        [b for exp in cv_data["experience"] for b in exp["bullets"]]
    )

    sem_score = 1
    # fasttext_similarity(
    #     cv_text,
    #     job_offer["description"]
    # )
    
    loc_score = location_score(
        job_offer
    )

    # Weighted total

    total = (
        0.4 * kw_score +
        0.3 * sem_score +
        0.3 * loc_score
    )

    return {
        "keyword_score": kw_score,
        "semantic_score": sem_score,
        "location_score": loc_score,
        "total_score": total
    }



# Apply scoring to ALL job offers
def apply_scoring():
    all_scores = {}
    for checksum, job_offer in job_offers.items():
        score = 5(cv_data, job_offer)
        all_scores[checksum] = score
        print(f"checksum: {checksum}, score: {score}")

    return all_scores


def apply_scores():
    output_file="/opt/airflow/output/jobs/jobs_with_scores.json"
    
    for checksum, job in job_offers.items():
        score = compute_total_score(cv_data, job) 
        job["match_score"] = score 

    with open(output_file, "w") as f:
        json.dump(job_offers, f, indent=2)

