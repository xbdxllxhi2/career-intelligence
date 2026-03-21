from sentence_transformers import SentenceTransformer, util


_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def match_profile_sections(profile, job_keywords, threshold=0.7):
    matched_skills = []
    matched_experience = []

    job_embeddings = get_model().encode(job_keywords, convert_to_tensor=True)

    for skill in profile.get("skills", []):
        skill_emb = get_model().encode(skill, convert_to_tensor=True)
        if any(util.pytorch_cos_sim(skill_emb, job_emb) > threshold for job_emb in job_embeddings):
            matched_skills.append(skill)

    for exp in profile.get("experience", []):
        for tag in exp.get("tags", []):
            tag_emb = get_model().encode(tag, convert_to_tensor=True)
            if any(util.pytorch_cos_sim(tag_emb, job_emb) > threshold for job_emb in job_embeddings):
                matched_experience.append(exp)
                break
    
    return {
        "keywords": job_keywords,
        "skills": matched_skills,
        "experience": matched_experience
    }
