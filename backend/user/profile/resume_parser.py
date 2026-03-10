"""
Resume Parser Service - Uses LLM to extract profile data from uploaded resumes.
"""
import logging
import os
import io
from typing import Optional
from flask.cli import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List

import fitz  # PyMuPDF for PDF parsing
import docx  # python-docx for Word documents

load_dotenv()

logger = logging.getLogger(__name__)

# Initialize the Groq client with OpenAI-compatible API
groq_client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY"),
)


class ParsedLanguage(BaseModel):
    name: str = ""
    proficiency: str = ""  # e.g., "Native", "Fluent", "B2", "Intermediate"


class ParsedEducation(BaseModel):
    degree: str = ""
    school: Optional[str] = None
    institution: Optional[str] = None
    year: Optional[str] = None
    coursework: Optional[str] = None


class ParsedExperience(BaseModel):
    title: str = ""
    company: Optional[str] = None
    period: Optional[str] = None
    location: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    bullets: List[str] = Field(default_factory=list)


class ParsedProject(BaseModel):
    name: str = ""
    description: Optional[str] = None
    url: Optional[str] = None
    year: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    bullets: List[str] = Field(default_factory=list)


class ParsedCertification(BaseModel):
    name: str = ""
    issuer: Optional[str] = None
    date: Optional[str] = None
    credentialId: Optional[str] = None
    url: Optional[str] = None


class ParsedProfile(BaseModel):
    """Structured output for parsed resume data"""
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    email: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    summary: Optional[str] = None
    education: List[ParsedEducation] = Field(default_factory=list)
    experience: List[ParsedExperience] = Field(default_factory=list)
    projects: List[ParsedProject] = Field(default_factory=list)
    certifications: List[ParsedCertification] = Field(default_factory=list)
    languages: List[ParsedLanguage] = Field(default_factory=list)


RESUME_PARSER_PROMPT = """You are an expert resume parser. Extract all relevant information from the resume and return it in a structured format.

Be thorough and extract:
- Personal info: first name, last name, email, phone, city, country
- Social links: LinkedIn URL, GitHub URL
- Professional summary
- Work experience: job title, company name, dates/period, location, key achievements (as bullet points), relevant technologies/skills used (as tags)
- Education: degree, institution/school, graduation year, relevant coursework
- Projects: project name, description, technologies used (as tags), key points (as bullets)
- Certifications: certification name, issuing organization, date, credential ID, URL
- Languages: language name and proficiency level as objects with "name" and "proficiency" fields (e.g., [{"name": "English", "proficiency": "Native"}, {"name": "French", "proficiency": "B2"}])

For experience and projects, extract specific achievements and technologies mentioned.
Return the structured data matching the ParsedProfile schema."""


class ResumeParserService:
    """Service for parsing resumes and extracting profile data using LLM."""

    def __init__(self):
        self.client = groq_client
        self.model = "openai/gpt-oss-120b"

    def extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file."""
        try:
            pdf_document = fitz.open(stream=file_content, filetype="pdf")
            text = ""
            for page in pdf_document:
                text += page.get_text()
            pdf_document.close()
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise ValueError(f"Failed to parse PDF: {str(e)}")

    def extract_text_from_docx(self, file_content: bytes) -> str:
        """Extract text from Word document."""
        try:
            doc = docx.Document(io.BytesIO(file_content))
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {e}")
            raise ValueError(f"Failed to parse Word document: {str(e)}")

    def extract_text(self, file_content: bytes, filename: str) -> str:
        """Extract text from uploaded file based on extension."""
        filename_lower = filename.lower()
        if filename_lower.endswith('.pdf'):
            return self.extract_text_from_pdf(file_content)
        elif filename_lower.endswith('.docx'):
            return self.extract_text_from_docx(file_content)
        elif filename_lower.endswith('.doc'):
            raise ValueError("Legacy .doc format is not supported. Please convert to .docx or .pdf")
        else:
            raise ValueError(f"Unsupported file format: {filename}")

    def parse_resume(self, file_content: bytes, filename: str) -> ParsedProfile:
        """Parse resume and extract structured profile data."""
        # Extract text from file
        resume_text = self.extract_text(file_content, filename)
        
        if not resume_text.strip():
            raise ValueError("Could not extract any text from the uploaded file")

        # Use LLM to parse the resume
        return self._parse_with_llm(resume_text)

    def _parse_with_llm(self, resume_text: str) -> ParsedProfile:
        """Use LLM to extract structured data from resume text using responses API."""
        try:
            response = self.client.responses.parse(
                model=self.model,
                instructions=RESUME_PARSER_PROMPT,
                input=f"Parse this resume and extract the profile data:\n\n{resume_text}",
                temperature=0.1,
                text_format=ParsedProfile,
            )
            
            logger.info(f"Resume parsed successfully")
            return response.output_parsed

        except Exception as e:
            logger.error(f"Error parsing resume with LLM: {e}")
            raise ValueError(f"Failed to parse resume: {str(e)}")
