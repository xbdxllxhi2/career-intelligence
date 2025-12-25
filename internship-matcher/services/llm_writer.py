import os
from groq import Groq
import logging
import json
from prompts.prompts_bank import *

logger = logging.getLogger(__name__)

client = Groq(api_key="")

def generate_cv_section(context):
    prompt =  get_PROMPT_V1_fr(context)

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="openai/gpt-oss-120b",
        temperature=0.2,
        max_tokens=50000  
    )

    logger.debug("llm response: %s", json.dumps(response.to_dict(), indent=4))

    return response.choices[0].message.content

