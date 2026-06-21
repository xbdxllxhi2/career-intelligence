from typing import Literal

from pydantic import BaseModel, Field


class CoverLetterResponse(BaseModel):
    """Structured cover letter / lettre de motivation content.

    Sender contact, date, recipient block and signature name come from the
    profile / job context and are not generated here.
    """

    language: Literal["en", "fr"] = Field(
        description="Language of the letter, matching the job offer."
    )
    subject: str = Field(
        description="Subject line, e.g. 'Application for the Data Engineering apprenticeship'."
    )
    salutation: str = Field(
        description="Greeting line, e.g. 'Dear Hiring Manager,' or 'Madame, Monsieur,'."
    )
    paragraphs: list[str] = Field(
        description="3 to 4 body paragraphs: hook, why-you, why-them/fit, call to action."
    )
    closing: str = Field(
        description="Closing line, e.g. 'Sincerely,' or a French formule de politesse."
    )
