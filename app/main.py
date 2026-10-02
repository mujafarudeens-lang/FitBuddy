from contextlib import asynccontextmanager

from fastapi import FastAPI

from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .database import init_db
from .routes import router


settings = get_settings()


@asynccontextmanager
async def lifespan(
    app: FastAPI
):

    init_db()

    yield


app = FastAPI(

    title=settings.app_name,

    version="1.0.0",

    description=(
        "AI-powered personalized "
        "7-day fitness plan generator "
        "using Gemini."
    ),

    lifespan=lifespan
)


app.mount(

    "/static",

    StaticFiles(
        directory="static"
    ),

    name="static"
)


app.include_router(
    router
)


@app.get(
    "/health"
)
def health():

    return {

        "status": "ok",

        "service":
            settings.app_name,

        "demo_mode":
            settings.demo_mode,

        "workout_model":
            settings.workout_model,

        "tip_model":
            settings.tip_model
    }