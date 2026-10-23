from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from database import getConnection
from database import initializeDatabase
from pydantic import BaseModel, Field
from typing import Literal
from fastapi import HTTPException
from main import scrapeInternships
from database import saveInternshipsToDatabase
import os

class PreferenceRequest(BaseModel):
    username: str
    internship_ids: list[int] = Field(min_length=1)
    status: Literal["saved", "hidden", "none"]


app = FastAPI(root_path=os.getenv("APP_ROOT_PATH", ""))

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

initializeDatabase()


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

@app.get("/api/internships")
def getInternships(
    username: str,
    keyword: str = "",
    company: str = "",
    location: str = "",
    view: str = "results"
):
    connection = getConnection()

    query = """
        SELECT i.*
        FROM internships i
        WHERE i.title LIKE ?
        AND i.company LIKE ?
        AND i.location LIKE ?
    """

    parameters = [
        f"%{keyword}%",
        f"%{company}%",
        f"%{location}%"
    ]

    if view == "results":
        query += """
            AND NOT EXISTS (
                SELECT 1
                FROM user_preferences p
                JOIN users u ON p.user_id = u.id
                WHERE p.internship_id = i.id
                AND u.username = ?
            )
        """

    elif view in ("saved", "hidden"):
        query += """
            AND EXISTS (
                SELECT 1
                FROM user_preferences p
                JOIN users u ON p.user_id = u.id
                WHERE p.internship_id = i.id
                AND u.username = ?
                AND p.status = ?
            )
        """

    parameters.append(username)

    if view in ("saved", "hidden"):
        parameters.append(view)

    query += " ORDER BY i.id DESC"

    try:
        rows = connection.execute(query, parameters).fetchall()
        return [dict(row) for row in rows]

    finally:
        connection.close()

@app.post("/api/preferences")
def updatePreferences(data: PreferenceRequest):
    username = data.username.strip()

    if not username:
        raise HTTPException(
            status_code=400,
            detail="Username cannot be empty."
        )

    connection = getConnection()

    try:
        connection.execute(
            "INSERT OR IGNORE INTO users (username) VALUES (?)",
            (username,)
        )

        user = connection.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        userId = user["id"]

        for internshipId in data.internship_ids:

            internship = connection.execute(
                "SELECT id FROM internships WHERE id = ?",
                (internshipId,)
            ).fetchone()

            if internship is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Internship {internshipId} not found."
                )

            if data.status == "none":
                connection.execute("""
                    DELETE FROM user_preferences
                    WHERE user_id = ? AND internship_id = ?
                """, (userId, internshipId))

            else:
                connection.execute("""
                    INSERT INTO user_preferences
                    (user_id, internship_id, status)
                    VALUES (?, ?, ?)

                    ON CONFLICT(user_id, internship_id)
                    DO UPDATE SET status = excluded.status
                """, (userId, internshipId, data.status))

        connection.commit()

        return {
            "message": "Preferences updated successfully.",
            "updated": len(data.internship_ids)
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

@app.post("/api/refresh")
def refreshInternships(company: str):
    internships = scrapeInternships(company)

    saveInternshipsToDatabase(internships)

    return {
        "message": "Internship search completed.",
        "found": len(internships)
    }