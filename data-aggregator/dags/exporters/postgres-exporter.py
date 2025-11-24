# from airflow import DAG
# from airflow.operators.python import PythonOperator
# from datetime import datetime
# import json
# from sqlalchemy import create_engine, Column, Integer, String, Boolean, JSON, ForeignKey, Float, TIMESTAMP, Text
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker, relationship

# JOBS_FILE_PATH = "/opt/airflow/output/jobs/jobs_with_scores.json"

# POSTGRES_CONN = ""

# Base = declarative_base()
# engine = create_engine(POSTGRES_CONN)
# Session = sessionmaker(bind=engine)


# class Organization(Base):
#     __tablename__ = "organizations"
#     organization_id = Column(Integer, primary_key=True)
#     name = Column(Text, unique=True, nullable=False)
#     logo_url = Column(Text)
#     website = Column(Text)
#     created_at = Column(TIMESTAMP, nullable=False, server_default="NOW()")

# class Job(Base):
#     __tablename__ = "jobs"
#     job_id = Column(Integer, primary_key=True)
#     job_title = Column(Text, nullable=False)
#     job_url = Column(Text, unique=True)
#     source = Column(Text, nullable=False)
#     location = Column(Text)
#     remote = Column(Boolean, default=False)
#     details = Column(JSON, nullable=False)
#     organization_id = Column(Integer, ForeignKey("organizations.organization_id", ondelete="SET NULL"))
#     job_checksum = Column(String(64), unique=True, nullable=False)
#     expires_at = Column(TIMESTAMP)
#     created_at = Column(TIMESTAMP, nullable=False, server_default="NOW()")
#     updated_at = Column(TIMESTAMP, nullable=False, server_default="NOW()")

#     scores = relationship("JobScore", back_populates="job")

# class JobScore(Base):
#     __tablename__ = "job_score"
#     id = Column(Integer, primary_key=True)
#     job_id = Column(Integer, ForeignKey("jobs.job_id", ondelete="CASCADE"))
#     metric = Column(Text, nullable=False)
#     factor = Column(Text)                  
#     value = Column(Float, nullable=False)
#     description = Column(Text)

#     job = relationship("Job", back_populates="scores")

# # Create tables
# Base.metadata.create_all(engine)


# def load_jobs_to_db():
#     with open(JOBS_FILE_PATH, "r") as f:
#         jobs_data = json.load(f)

#     session = Session()
#     for checksum, job in jobs_data.items():
#         org_name = job.get("organization")
#         org = session.query(Organization).filter_by(name=org_name).first()
#         if not org:
#             org = Organization(name=org_name, website=job.get("organization_url"), logo_url=job.get("organization_logo"))
#             session.add(org)
#             session.commit()

#         location = job["locations_raw"][0]["address"]["addressLocality"] if job.get("locations_raw") else None
#         remote = job.get("remote_derived", False)

#         job_obj = session.query(Job).filter_by(job_checksum=checksum).first()
#         if not job_obj:
#             job_obj = Job(
#                 job_title=job.get("title"),
#                 job_url=job.get("url"),
#                 source=job.get("source"),
#                 location=location,
#                 remote=remote,
#                 details=job,
#                 organization_id=org.organization_id,
#                 job_checksum=checksum
#             )
#             session.add(job_obj)
#             session.commit()

#         # Save scores if they exist
#         if "match_score" in job:
#             for metric, value in job["match_score"].items():
#                 score = JobScore(
#                     job_id=job_obj.job_id,
#                     metric=metric,
#                     value=value,
#                     description=f"{metric} score for job {job.get('title')}"
#                 )
#                 session.add(score)

#     session.commit()
#     session.close()



# # with DAG(
# #     "jobs_to_postgres",
# #     start_date=datetime(2025, 1, 1),
# #     schedule_interval="@daily",
# #     catchup=False,
# # ) as dag:

# #     load_jobs = PythonOperator(
# #         task_id="load_jobs",
# #         python_callable=load_jobs_to_db,
# #     )

# #     load_jobs
