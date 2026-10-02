from google.genai import types

from ..config import get_settings
from ..schemas import UserInput
from ..schemas import WorkoutPlan

from .gemini_client import get_client


def update_workout_plan(
    user: UserInput,
    original_plan: str,
    feedback: str
) -> WorkoutPlan:

    settings = get_settings()

    if settings.demo_mode:

        plan = WorkoutPlan.model_validate_json(
            original_plan
        )

        plan.summary = (
            f"{plan.summary} "
            f"Updated using user feedback: "
            f"{feedback}"
        )

        plan.safety_notes.append(
            "Demo update: production mode uses "
            "Gemini for the revision."
        )

        return plan

    client = get_client()

    prompt = f"""

You are revising an existing FitBuddy
7-day workout plan.

USER INFORMATION

Name:
{user.name}

Age:
{user.age}

Weight:
{user.weight} kg

Goal:
{user.goal}

Intensity:
{user.intensity}

Experience:
{user.experience_level}


ORIGINAL PLAN

{original_plan}


USER FEEDBACK

{feedback}


TASK

Revise the workout plan so that it
addresses the user's feedback.

Preserve:

- fitness goal
- appropriate intensity
- experience level
- recovery
- safety

Return exactly 7 days.

Each day must contain:

- day
- focus
- warmup
- exercises
- cooldown

Each exercise must contain:

- name
- sets
- reps_or_duration
- rest
- notes

Do not diagnose injuries.

Do not prescribe medical treatment.
"""

    response = client.models.generate_content(

        model=settings.workout_model,

        contents=prompt,

        config=types.GenerateContentConfig(

            response_mime_type="application/json",

            response_schema=WorkoutPlan,

            temperature=0.4
        )
    )

    if not response.text:

        raise RuntimeError(
            "Gemini returned an empty updated plan."
        )

    return WorkoutPlan.model_validate_json(
        response.text
    )