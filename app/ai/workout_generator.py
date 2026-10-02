from google.genai import types

from ..config import get_settings
from ..schemas import UserInput
from ..schemas import WorkoutPlan

from .gemini_client import get_client


def _demo_plan(
    user: UserInput
) -> WorkoutPlan:

    focuses = [

        (
            "Day 1",
            "Full Body Strength"
        ),

        (
            "Day 2",
            "Cardio + Core"
        ),

        (
            "Day 3",
            "Lower Body"
        ),

        (
            "Day 4",
            "Recovery + Mobility"
        ),

        (
            "Day 5",
            "Upper Body"
        ),

        (
            "Day 6",
            "Full Body Conditioning"
        ),

        (
            "Day 7",
            "Rest + Stretching"
        ),
    ]

    days = []

    for day, focus in focuses:

        days.append({

            "day": day,

            "focus": focus,

            "warmup":
                "5–10 minutes of easy movement "
                "and dynamic mobility.",

            "exercises": [

                {
                    "name":
                        "Bodyweight Squat",

                    "sets":
                        "3",

                    "reps_or_duration":
                        "10–12 reps",

                    "rest":
                        "60–90 sec",

                    "notes":
                        "Controlled tempo"
                },

                {
                    "name":
                        "Incline Push-up",

                    "sets":
                        "3",

                    "reps_or_duration":
                        "8–12 reps",

                    "rest":
                        "60–90 sec",

                    "notes":
                        "Use a stable surface"
                },

                {
                    "name":
                        "Plank",

                    "sets":
                        "3",

                    "reps_or_duration":
                        "20–40 sec",

                    "rest":
                        "45–60 sec",

                    "notes":
                        "Keep a neutral spine"
                }
            ],

            "cooldown":
                "5 minutes of easy walking "
                "and gentle stretching."
        })

    return WorkoutPlan(

        title=
            f"7-Day {user.goal.title()} Plan",

        summary=
            f"A {user.intensity}-intensity "
            f"starter plan for {user.name} "
            f"with {user.experience_level} "
            f"experience.",

        days=days,

        safety_notes=[

            "Stop if you feel sharp pain, "
            "dizziness, chest pain, or unusual "
            "shortness of breath.",

            "Adjust exercise difficulty to your "
            "current ability and recover between "
            "sessions."
        ]
    )


def generate_workout_gemini(
    user: UserInput
) -> WorkoutPlan:

    settings = get_settings()

    if settings.demo_mode:

        return _demo_plan(user)

    client = get_client()

    prompt = f"""

You are FitBuddy, a conservative
fitness-planning assistant.

Create a practical 7-day workout plan
for this user.

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

Requirements:

1. Return exactly 7 days.

2. Every day must contain:
   - warm-up
   - exercises
   - cooldown or recovery

3. Every exercise needs:
   - name
   - sets
   - reps_or_duration
   - rest
   - notes

4. Respect the selected intensity.

5. Respect the user's experience level.

6. Include recovery appropriately.

7. Do not diagnose injuries.

8. Do not prescribe medical treatment.

9. Keep recommendations general and safe.

10. Make the plan easy to follow.
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
            "Gemini returned an empty workout plan."
        )

    return WorkoutPlan.model_validate_json(
        response.text
    )