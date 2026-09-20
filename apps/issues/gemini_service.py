

from django.conf import settings

from google import genai


def get_gemini_client():
    """
    Create and return a Gemini API client.
    """

    if not settings.GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is not configured."
        )

    return genai.Client(
        api_key=settings.GEMINI_API_KEY
    )


def analyze_civic_issue(problem):
    """
    Analyze a citizen's civic issue using Gemini.
    """

    client = get_gemini_client()

    prompt = f"""
You are JanMitra, an AI assistant that helps citizens
report civic issues in Bengaluru.

Analyze the citizen's problem below.

Citizen problem:
{problem}

Choose exactly one category from:

- Road & Pathhole
- Streetlight
- Garbage and Sanitation
- Water Supply
- Drainage Problem
- Electricity issue
- Traffic Problem
- Other

Return the response in exactly this format:

CATEGORY: <category>
TITLE: <short issue title>
REASON: <one short sentence explaining the category>

Rules:

- CATEGORY must be exactly one of the listed values.
- TITLE must be concise and suitable for a civic issue report.
- REASON must be one short sentence.
- Do not add any extra text.
"""

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
    )

    return response.text.strip()


def ask_gemini(prompt):
    """
    Generic Gemini text generation helper.
    """

    client = get_gemini_client()

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
    )

    return response.text.strip()