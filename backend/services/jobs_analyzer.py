import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from repositories.jobs_repository import *
import logging

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from services.keyword_extractor import get_job_required_skills, extract_job_skills

logger = logging.getLogger(__name__)

import pandas as pd

KNOWN_SKILLS = [
    # Programming languages
    "Bash", "Java", "Python", "SQL",
    
    # Backend frameworks
    "Hibernate", "Jakarta EE", "JPA", "REST API design", "Spring Boot", "Spring Security",
    
    # Identity & Access Management
    "ABAC", "Identity Provider Integration", "JWT", "Keycloak", "Keycloak Event Listener SPI",
    "OAuth2", "RBAC", "SSO", "User Federation", "OpenID Connect",
    
    # Data Engineering
    "Apache Airflow", "Batch processing", "Data ingestion", "Data modeling", "Data quality",
    "Data transformation", "ETL/ELT pipelines", "Oracle SQL", "PostgreSQL", "Scheduling",
    "Workflow orchestration",
    
    # NLP & Search
    "Cosine similarity", "Keyword extraction", "NER", "RAG (Retrieval-Augmented Generation)",
    "Semantic search", "Sentence Embeddings", "TF-IDF", "spaCy", "Transformers",
    
    # Quantitative Analysis
    "Actualisation de flux (DCF)", "Analyse de volatilité", "Black-Scholes", "Gordon Growth Model (GGM)",
    "Modèles stochastiques", "Modélisation financière", "Pricing d’options", "Sensibilité Delta/Gamma/Vega", "WACC",
    
    # Blockchain
    "EVM", "Ethereum", "PoC remplacement d’un CBS par validateur Ethereum",
    "Settlement on-chain", "Smart Contracts", "Transactions et gas optimization",
    
    # Cloud & DevOps
    "Argo CD", "Cluster deployment", "Docker", "GitLab CI/CD", "Helm", "Kubernetes", "Linux", "Terraform",
    
    # Event-driven architecture
    "Asynchronous messaging", "Event sourcing", "Kafka", "Outbox Pattern", "Real-time streaming",
    
    # Tools
    "BPMN", "Git", "IntelliJ", "ISO20022", "Jenkins", "Kibana", "Maven", "Mermaid",
    
    # Soft skills
    "Adaptabilité", "Analyse", "Autonomie", "Collaboration", "Communication",
    "Leadership", "Organisation", "Proactivité", "Rigueur", "Résolution de problèmes", "Travail d’équipe"
]


def build_company_skill_matrix(jobs, my_skills, known_skills=KNOWN_SKILLS):
    rows = []

    for job in jobs:
        company = job.get("organization", "Unknown")
        description = job.get("description_text")
        job_skills = extract_job_skills(description, known_skills)

        for skill in job_skills:
            if skill in my_skills:
                rows.append({"company": company, "skill": skill})

    df = pd.DataFrame(rows)

    if df.empty:
        raise Exception("Data frame is empty")

    pivot = pd.pivot_table(
        df,
        index="skill",
        columns="company",
        aggfunc="size",
        fill_value=0
    )

    pivot["total_jobs"] = pivot.sum(axis=1)
 
    plt.figure(figsize=(14,6))
    sns.heatmap(pivot, annot=True, fmt="d", cmap="Blues")
    plt.title("Companies Most Requesting My Skills")
    plt.show()




def perform_kmeans():
    jobs_list = get_all_raw_jobs()

    df = pd.DataFrame(jobs_list)

    # Extract total score and other scores
    df["total_score"] = df["match_score"].apply(lambda x: x.get("total_score", 0))
    df["keyword_score"] = df["match_score"].apply(lambda x: x.get("keyword_score", 0))
    df["semantic_score"] = df["match_score"].apply(lambda x: x.get("semantic_score", 0))
    df["location_score"] = df["match_score"].apply(lambda x: x.get("location_score", 0))

    # Extract first location if available
    df["location"] = df["locations_raw"].apply(lambda x: x[0].get("address", {}).get("addressLocality") if x else "Unknown")

    #adjust clusters number
    unique_points = df[["total_score", "keyword_score", "semantic_score", "location_score"]].drop_duplicates()
    n_clusters = min(3, len(unique_points))

    score_cols = ["total_score", "keyword_score", "semantic_score", "location_score"]
    X = df[score_cols].fillna(0)
    
    # Scale the data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Fit K-Means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    df["cluster"] = kmeans.fit_predict(X_scaled)
    
     # Plot
    plt.figure(figsize=(8, 6))
    plt.scatter(
        df["total_score"],
        df["semantic_score"],
        c=df["cluster"],
        cmap="viridis",
        s=60,
        edgecolor="black"
    )

    plt.xlabel("Total Score")
    plt.ylabel("Semantic Score")
    plt.title("K-Means Clustering of Jobs Based on Score Components")

    # Show centroids
    centers = kmeans.cluster_centers_
    plt.scatter(
        centers[:, 0], centers[:, 2], 
        c="red", s=200, marker="X"
    )

    plt.grid(True)
    plt.show(block=True)

    return df

def analyze_jobs():
    jobs_list = get_all_raw_jobs()
    logger.debug("Got jobs %s",jobs_list)

    df = pd.DataFrame(jobs_list)

    df["total_score"] = df["match_score"].apply(lambda x: x.get("total_score", 0))
    df["location"] =  df["locations_raw"].apply(lambda x: x[0].get("address").get("addressLocality"))

    # --- Plots ---
    # plt.ion() 

    # 1. Histogram of scores
    plt.figure(figsize=(8,4))
    plt.hist(df["total_score"], bins=10, color="skyblue", edgecolor="black")
    plt.title("Distribution of Job Scores")
    plt.xlabel("total_score")
    plt.ylabel("Number of Jobs")
    plt.show()

    # 2. Bar chart of top companies
    top_companies = df["organization"].value_counts().head(10)
    plt.figure(figsize=(8,6))
    top_companies.plot(kind="barh", color="lightgreen")
    plt.title("Top 10 Companies by Job Count")
    plt.xlabel("Number of Jobs")
    plt.ylabel("Company")
    plt.show()

    # 3. Pie chart of employment type
    emp_counts = df["employment_type"].value_counts()
    plt.figure(figsize=(6,6))
    emp_counts.plot(kind="pie", autopct="%1.1f%%")
    plt.title("Employment Type Distribution")
    plt.ylabel("")
    plt.show()

    # 4. Boxplot
    top5_companies = df["organization"].value_counts().head(5).index
    plt.figure(figsize=(10,6))
    sns.boxplot(x="total_score", y="organization", data=df[df["organization"].isin(top5_companies)])
    plt.title("Score Distribution by Top 5 Companies")
    plt.show()

