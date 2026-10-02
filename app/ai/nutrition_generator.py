from google.genai import types

from ..config import get_settings
from ..schemas import NutritionTip
from ..schemas import UserInput

from .gemini_client import get_client


def _demo_tip(
    user: UserInput
) -> NutritionTip:

    if user.goal == "muscle gain":

        tip = (
            "Include a protein-rich food in each "
            "main meal, such as eggs, fish, chicken, "
            "beans, tofu, or Greek yogurt."
        )

    elif user.goal == "weight loss":

        tip = (
            "Build meals around vegetables, a "
            "protein source, and high-fiber "
            "carbohydrates while keeping portions "
            "appropriate for your needs."
        )

    elif user.goal == "endurance":

        tip = (
            "Prioritize regular hydration and "
            "include carbohydrate-rich foods "
            "around longer training sessions."
        )

    elif user.goal == "flexibility":

        tip = (
            "Stay hydrated and include a varied "
            "diet with protein, vegetables, fruits, "
            "and whole grains to support recovery."
        )

    else:

        tip = (
            "Aim for balanced meals with protein, "
            "vegetables or fruit, whole grains, "
            "and adequate fluids."
        )

    return NutritionTip(

        tip=tip,

        hydration=(
            "Drink fluids regularly and increase "
            "intake when training or sweating more."
        ),

        recovery=(
            "Prioritize regular sleep and adequate "
            "food intake to support recovery."
        )
    )


def generate_nutrition_tip_with_flash(
    user: UserInput
) -> NutritionTip:

    settings = get_settings()

    if settings.demo_mode:

        return _demo_tip(user)

    client = get_client()

    prompt = f"""

Give concise wellness nutrition and recovery
guidance for this user.

Goal:
{user.goal}

Intensity:
{user.intensity}

Experience:
{user.experience_level}

Age:
{user.age}

Return:

1. One practical nutrition tip.
2. One hydration suggestion.
3. One recovery suggestion.

Do not provide medical treatment.

Do not diagnose conditions.

Do not prescribe supplements.
"""

    response = client.models.generate_content(

        model=settings.tip_model,

        contents=prompt,

        config=types.GenerateContentConfig(

            response_mime_type="application/json",

            response_schema=NutritionTip,

            temperature=0.3
        )
    )

    if not response.text:

        raise RuntimeError(
            "Gemini returned an empty nutrition tip."
        )

    return NutritionTip.model_validate_json(
        response.text
    )