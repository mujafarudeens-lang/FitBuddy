def sample_user():

    return {

        "user_id":
            "test01",

        "name":
            "Test User",

        "age":
            24,

        "weight":
            70,

        "goal":
            "muscle gain",

        "intensity":
            "medium",

        "experience_level":
            "beginner"
    }


def test_health(client):

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert (
        response.json()["status"]
        == "ok"
    )


def test_home(client):

    response = client.get("/")

    assert response.status_code == 200

    assert "FitBuddy" in response.text


def test_generate_api(client):

    response = client.post(

        "/api/v1/plans/generate",

        json=sample_user()
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["user"]["user_id"]
        == "test01"
    )

    assert (
        len(
            data["plan"]
            ["original_plan"]
            ["days"]
        )
        == 7
    )


def test_feedback_api(client):

    client.post(

        "/api/v1/plans/generate",

        json=sample_user()
    )


    response = client.post(

        "/api/v1/plans/feedback",

        json={

            "user_id":
                "test01",

            "feedback":
                "Add more cardio."
        }
    )


    assert response.status_code == 200


    assert (
        response.json()
        ["plan"]
        ["updated_plan"]
        is not None
    )


def test_admin(client):

    client.post(

        "/api/v1/plans/generate",

        json=sample_user()
    )


    response = client.get(

        "/view-all-users"
        "?admin_key=test-admin"
    )


    assert response.status_code == 200

    assert (
        "Test User"
        in response.text
    )


def test_validation(client):

    bad_user = sample_user()

    bad_user["age"] = 5


    response = client.post(

        "/api/v1/plans/generate",

        json=bad_user
    )


    assert response.status_code == 422