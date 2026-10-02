import os
from functools import lru_cache

from dotenv import load_dotenv


load_dotenv()


class Settings:

    app_name = os.getenv(
        "APP_NAME",
        "FitBuddy"
    )

    gemini_api_key = os.getenv(
        "GEMINI_API_KEY",
        ""
    ).strip()

    workout_model = os.getenv(
        "GEMINI_WORKOUT_MODEL",
        "gemini-2.5-pro"
    ).strip()

    tip_model = os.getenv(
        "GEMINI_TIP_MODEL",
        "gemini-2.5-flash-lite"
    ).strip()

    demo_mode = os.getenv(
        "DEMO_MODE",
        "true"
    ).strip().lower() in {
        "1",
        "true",
        "yes",
        "on"
    }

    database_url = os.getenv(
        "DATABASE_URL",
        "sqlite:///./fitbuddy.db"
    ).strip()

    admin_key = os.getenv(
        "ADMIN_KEY",
        "change-this-admin-key"
    ).strip()


@lru_cache
def get_settings():

    return Settings()