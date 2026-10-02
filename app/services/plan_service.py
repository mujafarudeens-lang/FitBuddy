import json
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..ai.nutrition_generator import (
    generate_nutrition_tip_with_flash
)

from ..ai.plan_updater import (
    update_workout_plan
)

from ..ai.workout_generator import (
    generate_workout_gemini
)

from ..models import User
from ..models import WorkoutPlan

from ..schemas import FeedbackRequest
from ..schemas import UserInput


def save_or_update_user(
    db: Session,
    data: UserInput
) -> User:

    user = db.scalar(
        select(User).where(
            User.user_id == data.user_id
        )
    )

    if user is None:

        user = User(

            user_id=data.user_id,

            name=data.name,

            age=data.age,

            weight=data.weight,

            goal=data.goal,

            intensity=data.intensity,

            experience_level=
                data.experience_level
        )

        db.add(user)

        db.flush()

    else:

        user.name = data.name

        user.age = data.age

        user.weight = data.weight

        user.goal = data.goal

        user.intensity = data.intensity

        user.experience_level = (
            data.experience_level
        )

    return user


def generate_and_save_plan(
    db: Session,
    data: UserInput
):

    user = save_or_update_user(
        db,
        data
    )

    workout = generate_workout_gemini(
        data
    )

    tip = generate_nutrition_tip_with_flash(
        data
    )

    existing = db.scalar(

        select(WorkoutPlan)
        .where(
            WorkoutPlan.user_id == user.id
        )
    )

    if existing:

        existing.original_plan = (
            workout.model_dump_json(
                indent=2
            )
        )

        existing.updated_plan = None

        existing.nutrition_tip = (
            tip.model_dump_json(
                indent=2
            )
        )

        existing.feedback = None

        plan = existing

    else:

        plan = WorkoutPlan(

            user_id=user.id,

            original_plan=
                workout.model_dump_json(
                    indent=2
                ),

            nutrition_tip=
                tip.model_dump_json(
                    indent=2
                )
        )

        db.add(plan)

    db.commit()

    db.refresh(user)

    db.refresh(plan)

    return user, plan


def update_plan_from_feedback(
    db: Session,
    request: FeedbackRequest
):

    user = db.scalar(

        select(User).where(
            User.user_id == request.user_id
        )
    )

    if not user:

        raise LookupError(
            "User not found."
        )

    plan = db.scalar(

        select(WorkoutPlan)
        .where(
            WorkoutPlan.user_id == user.id
        )
        .order_by(
            WorkoutPlan.id.desc()
        )
    )

    if not plan:

        raise LookupError(
            "No workout plan found for this user."
        )

    data = UserInput(

        user_id=user.user_id,

        name=user.name,

        age=user.age,

        weight=user.weight,

        goal=user.goal,

        intensity=user.intensity,

        experience_level=
            user.experience_level
    )

    revised = update_workout_plan(

        data,

        plan.original_plan,

        request.feedback
    )

    plan.updated_plan = (
        revised.model_dump_json(
            indent=2
        )
    )

    plan.feedback = request.feedback

    db.commit()

    db.refresh(plan)

    return user, plan


def plan_to_dict(
    plan: WorkoutPlan
):

    return {

        "id":
            plan.id,

        "original_plan":
            json.loads(
                plan.original_plan
            ),

        "updated_plan":
            (
                json.loads(
                    plan.updated_plan
                )
                if plan.updated_plan
                else None
            ),

        "nutrition_tip":
            json.loads(
                plan.nutrition_tip
            ),

        "feedback":
            plan.feedback,

        "created_at":
            (
                plan.created_at.isoformat()
                if plan.created_at
                else None
            ),

        "updated_at":
            (
                plan.updated_at.isoformat()
                if plan.updated_at
                else None
            )
    }