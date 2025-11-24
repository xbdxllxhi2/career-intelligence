from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

def match_profile_sections(profile, job_keywords, threshold=0.5):
    matched_skills = []
    matched_experience = []

    job_embeddings = model.encode(job_keywords, convert_to_tensor=True)

    for skill in profile.get("skills", []):
        skill_emb = model.encode(skill, convert_to_tensor=True)
        if any(util.pytorch_cos_sim(skill_emb, job_emb) > threshold for job_emb in job_embeddings):
            matched_skills.append(skill)

    for exp in profile.get("experience", []):
        for tag in exp.get("tags", []):
            tag_emb = model.encode(tag, convert_to_tensor=True)
            if any(util.pytorch_cos_sim(tag_emb, job_emb) > threshold for job_emb in job_embeddings):
                matched_experience.append(exp)
                break

    return {
        "keywords": job_keywords,
        "skills": matched_skills,
        "experience": matched_experience
    }
