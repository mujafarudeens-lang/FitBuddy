from typing import Literal
from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator


Goal = Literal[
    "weight loss",
    "muscle gain",
    "general wellness",
    "flexibility",
    "endurance"
]

Intensity = Literal[
    "low",
    "medium",
    "high"
]

Experience = Literal[
    "beginner",
    "intermediate",
    "advanced"
]


class UserInput(BaseModel):

    user_id: str = Field(
        min_length=2,
        max_length=80
    )

    name: str = Field(
        min_length=2,
        max_length=120
    )

    age: int = Field(
        ge=13,
        le=100
    )

    weight: float = Field(
        gt=20,
        le=400
    )

    goal: Goal

    intensity: Intensity

    experience_level: Experience = "beginner"

    @field_validator(
        "user_id",
        "name"
    )
    @classmethod
    def clean_text(cls, value: str):

        return " ".join(
            value.strip().split()
        )


class FeedbackRequest(BaseModel):

    user_id: str = Field(
        min_length=2,
        max_length=80
    )

    feedback: str = Field(
        min_length=3,
        max_length=2000
    )


class Exercise(BaseModel):

    name: str

    sets: str

    reps_or_duration: str

    rest: str

    notes: str = ""


class DayPlan(BaseModel):

    day: str

    focus: str

    warmup: str

    exercises: list[Exercise]

    cooldown: str


class WorkoutPlan(BaseModel):

    title: str

    summary: str

    days: list[DayPlan] = Field(
        min_length=7,
        max_length=7
    )

    safety_notes: list[str] = Field(
        default_factory=list
    )


class NutritionTip(BaseModel):

    tip: str

    hydration: str

    recovery: str