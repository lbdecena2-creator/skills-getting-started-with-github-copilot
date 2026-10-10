"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Practice team play, drills, and weekend matches",
        "schedule": "Wednesdays and Saturdays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": []
    },
    "Basketball Club": {
        "description": "Improve shooting, defense, and game strategy",
        "schedule": "Tuesdays and Thursdays, 3:45 PM - 5:00 PM",
        "max_participants": 14,
        "participants": []
    },
    "Drama Club": {
        "description": "Explore acting, scenes, and live performance techniques",
        "schedule": "Mondays and Thursdays, 3:30 PM - 4:45 PM",
        "max_participants": 16,
        "participants": []
    },
    "Art Studio": {
        "description": "Create paintings, sketches, and mixed-media artwork",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": []
    },
    "Science Olympiad": {
        "description": "Solve scientific problems and compete in team challenges",
        "schedule": "Tuesdays and Fridays, 3:30 PM - 4:45 PM",
        "max_participants": 12,
        "participants": []
    },
    "Debate Team": {
        "description": "Develop public speaking, argumentation, and research skills",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 10,
        "participants": []
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities(response: Response):
    response.headers["Cache-Control"] = "no-store"
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]
    normalized_email = email.strip().lower()

    # Prevent duplicate registrations and over-capacity signups
    if any(participant.strip().lower() == normalized_email for participant in activity["participants"]):
        raise HTTPException(status_code=400, detail=f"{email} is already signed up for {activity_name}")

    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail=f"{activity_name} is full")

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/signup")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]
    normalized_email = email.strip().lower()
    participant_index = next(
        (
            index
            for index, participant in enumerate(activity["participants"])
            if participant.strip().lower() == normalized_email
        ),
        None,
    )
    if participant_index is None:
        raise HTTPException(
            status_code=404,
            detail=f"{email} is not signed up for {activity_name}",
        )

    activity["participants"].pop(participant_index)
    return {"message": f"Unregistered {email} from {activity_name}"}
