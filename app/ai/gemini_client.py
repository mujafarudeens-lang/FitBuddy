from functools import lru_cache

from google import genai

from ..config import get_settings


@lru_cache
def get_client():

    settings = get_settings()

    if not settings.gemini_api_key:

        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    client = genai.Client(
        api_key=settings.gemini_api_key
    )

    return client