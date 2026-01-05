import os
from groq import Groq
import logging
import json
from openai import OpenAI
from prompts.prompts_bank import *
from models.llm_resume_generation_response import ResumeGenerationResponse


logger = logging.getLogger(__name__)


client = Groq(api_key="{key here}")
open_Ai_client = OpenAI(api_key="{key here}")
groq_open_ai_client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key="")


def _build_messages(context):
    return [{"role": "system", "content": get_PROMPT_V3_fr(context)}]

def _log_response(response):
    logger.info("llm response: %s", json.dumps(response.to_dict(), indent=4))
    return response


def _groq_open_api_oss_120b_generate_resume_section(context):
    response = groq_open_ai_client.responses.parse(
        model="openai/gpt-oss-120b",
        temperature=0.2,
        instructions=get_PROMPT_V5_fr(context),
        input=f"description {context['job_description']}\n profile {context['profile']}",
        # max_tokens=5000,
        text_format= ResumeGenerationResponse
    )
    return _log_response(response).output_parsed


def _open_api_5_mini_generate_resume_section(context):
    response = open_Ai_client.responses.parse(
        instructions="Generate a detailed resume section based on the provided context.",
        input= _build_messages(context),
        model="gpt-5-mini",
        # temperature=0.2,
        text_format= ResumeGenerationResponse,
        max_completion_tokens=5000,
    )
    return _log_response(response).output_parsed


def _open_api_oss_120b_generate_resume_section(context):
    response = client.chat.completions.create(
        messages=_build_messages(context),
        model="openai/gpt-oss-120b",
        temperature=0.2,
        max_tokens=50000  
    )
    return _log_response(response).choices[0].message.content



def generate_cv_section(context):
    return _groq_open_api_oss_120b_generate_resume_section(context)