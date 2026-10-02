import json

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi import HTTPException
from fastapi import Request

from fastapi.responses import HTMLResponse

from fastapi.templating import Jinja2Templates

from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import get_settings
from .database import get_db
from .models import User
from .models import WorkoutPlan

from .schemas import FeedbackRequest
from .schemas import UserInput

from .services.plan_service import (
    generate_and_save_plan,
    plan_to_dict,
    update_plan_from_feedback
)


router = APIRouter()

templates = Jinja2Templates(
    directory="templates"
)

settings = get_settings()


def _user_context(
    user,
    plan
):

    return {

        "user": user,

        "plan": plan,

        "original":
            json.loads(
                plan.original_plan
            ),

        "updated":
            (
                json.loads(
                    plan.updated_plan
                )
                if plan.updated_plan
                else None
            ),

        "nutrition":
            json.loads(
                plan.nutrition_tip
            )
    }


@router.get(
    "/",
    response_class=HTMLResponse
)
def home(
    request: Request
):

    return templates.TemplateResponse(

        "index.html",

        {
            "request": request
        }
    )


@router.post(
    "/generate-workout",
    response_class=HTMLResponse
)
def generate_workout(

    request: Request,

    user_id: str = Form(...),

    name: str = Form(...),

    age: int = Form(...),

    weight: float = Form(...),

    goal: str = Form(...),

    intensity: str = Form(...),

    experience_level: str = Form(
        "beginner"
    ),

    db: Session = Depends(get_db)
):

    try:

        data = UserInput(

            user_id=user_id,

            name=name,

            age=age,

            weight=weight,

            goal=goal,

            intensity=intensity,

            experience_level=
                experience_level
        )

        user, plan = (
            generate_and_save_plan(
                db,
                data
            )
        )

        return templates.TemplateResponse(

            "result.html",

            {
                "request": request,
                **_user_context(
                    user,
                    plan
                )
            }
        )

    except Exception as exc:

        return templates.TemplateResponse(

            "index.html",

            {
                "request": request,
                "error": str(exc)
            },

            status_code=400
        )


@router.post(
    "/submit-feedback",
    response_class=HTMLResponse
)
def submit_feedback(

    request: Request,

    user_id: str = Form(...),

    feedback: str = Form(...),

    db: Session = Depends(get_db)
):

    try:

        user, plan = (
            update_plan_from_feedback(

                db,

                FeedbackRequest(

                    user_id=user_id,

                    feedback=feedback
                )
            )
        )

        return templates.TemplateResponse(

            "result.html",

            {
                "request": request,

                **_user_context(
                    user,
                    plan
                ),

                "message":
                    "Your plan has been updated "
                    "based on your feedback."
            }
        )

    except LookupError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )


@router.get(
    "/view-all-users",
    response_class=HTMLResponse
)
def view_all_users(

    request: Request,

    admin_key: str | None = None,

    db: Session = Depends(get_db)
):

    if (
        settings.admin_key
        and admin_key != settings.admin_key
    ):

        return templates.TemplateResponse(

            "all_users.html",

            {
                "request": request,

                "authorized": False,

                "error":
                    "Enter the correct admin key."
            },

            status_code=403
        )

    users = db.scalars(

        select(User)
        .order_by(
            User.created_at.desc()
        )

    ).all()

    rows = []

    for user in users:

        plan = db.scalar(

            select(WorkoutPlan)

            .where(
                WorkoutPlan.user_id == user.id
            )

            .order_by(
                WorkoutPlan.id.desc()
            )
        )

        rows.append({

            "user": user,

            "plan": plan
        })

    return templates.TemplateResponse(

        "all_users.html",

        {
            "request": request,

            "authorized": True,

            "rows": rows
        }
    )


# =========================
# REST API
# =========================


@router.post(
    "/api/v1/plans/generate"
)
def api_generate(

    data: UserInput,

    db: Session = Depends(get_db)
):

    try:

        user, plan = (
            generate_and_save_plan(
                db,
                data
            )
        )

        return {

            "user": {

                "id": user.id,

                "user_id":
                    user.user_id,

                "name":
                    user.name
            },

            "plan":
                plan_to_dict(plan)
        }

    except Exception as exc:

        raise HTTPException(

            status_code=400,

            detail=str(exc)
        )


@router.post(
    "/api/v1/plans/feedback"
)
def api_feedback(

    data: FeedbackRequest,

    db: Session = Depends(get_db)
):

    try:

        user, plan = (
            update_plan_from_feedback(
                db,
                data
            )
        )

        return {

            "user": {

                "id": user.id,

                "user_id":
                    user.user_id,

                "name":
                    user.name
            },

            "plan":
                plan_to_dict(plan)
        }

    except LookupError as exc:

        raise HTTPException(

            status_code=404,

            detail=str(exc)
        )

    except Exception as exc:

        raise HTTPException(

            status_code=400,

            detail=str(exc)
        )


@router.get(
    "/api/v1/users"
)
def api_users(
    db: Session = Depends(get_db)
):

    users = db.scalars(

        select(User)
        .order_by(
            User.created_at.desc()
        )

    ).all()

    return [

        {

            "id":
                user.id,

            "user_id":
                user.user_id,

            "name":
                user.name,

            "age":
                user.age,

            "weight":
                user.weight,

            "goal":
                user.goal,

            "intensity":
                user.intensity,

            "experience_level":
                user.experience_level,

            "created_at":
                user.created_at.isoformat()
        }

        for user in users
    ]


@router.get(
    "/api/v1/users/{user_id}"
)
def api_user(

    user_id: str,

    db: Session = Depends(get_db)
):

    user = db.scalar(

        select(User)
        .where(
            User.user_id == user_id
        )
    )

    if not user:

        raise HTTPException(

            status_code=404,

            detail="User not found."
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

    return {

        "user": {

            "id":
                user.id,

            "user_id":
                user.user_id,

            "name":
                user.name,

            "age":
                user.age,

            "weight":
                user.weight,

            "goal":
                user.goal,

            "intensity":
                user.intensity,

            "experience_level":
                user.experience_level
        },

        "plan":
            (
                plan_to_dict(plan)
                if plan
                else None
            )
    }


@router.get(
    "/api/v1/plans/{user_id}"
)
def api_plan(

    user_id: str,

    db: Session = Depends(get_db)
):

    user = db.scalar(

        select(User)
        .where(
            User.user_id == user_id
        )
    )

    if not user:

        raise HTTPException(

            status_code=404,

            detail="User not found."
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

        raise HTTPException(

            status_code=404,

            detail="Plan not found."
        )

    return plan_to_dict(plan)