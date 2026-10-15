
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, root_validator, validator
from typing import Optional
import sqlite3
import re

app = FastAPI(
    title="Students Database CRUD API",
    description="Student records management using FastAPI and SQLite",
    version="1.0.0"
)

DATABASE = "students.db"


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                date_of_birth TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                course TEXT,
                address TEXT
            )
        """)


initialize_database()


class StudentCreate(BaseModel):
    student_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    date_of_birth: str = Field(..., min_length=1)
    email: Optional[str] = None
    phone: Optional[str] = None
    course: Optional[str] = None
    address: Optional[str] = None

    @validator("email")
    def validate_email(cls, value):
        if value and not re.match(
            r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value
        ):
            raise ValueError("Invalid email address")
        return value

    @root_validator
    def require_contact(cls, values):
        if not values.get("email") and not values.get("phone"):
            raise ValueError("Provide an email or phone number")
        return values


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    date_of_birth: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    course: Optional[str] = None
    address: Optional[str] = None

    @validator("email")
    def validate_email(cls, value):
        if value and not re.match(
            r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value
        ):
            raise ValueError("Invalid email address")
        return value


@app.get("/")
def home():
    return {"message": "Students Database CRUD API is running"}


@app.post("/students", status_code=201)
def create_student(student: StudentCreate):
    try:
        with get_connection() as conn:
            conn.execute("""
                INSERT INTO students
                (student_id, name, date_of_birth, email,
                 phone, course, address)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                student.student_id, student.name,
                student.date_of_birth, student.email,
                student.phone, student.course, student.address
            ))
        return {
            "message": "Student created successfully",
            "student_id": student.student_id
        }
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Student ID already exists"
        )


@app.get("/students")
def list_students(
    name: Optional[str] = Query(default=None),
    course: Optional[str] = Query(default=None)
):
    query = "SELECT * FROM students WHERE 1=1"
    params = []

    if name:
        query += " AND name LIKE ?"
        params.append(f"%{name}%")

    if course:
        query += " AND course LIKE ?"
        params.append(f"%{course}%")

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()

    return [dict(row) for row in rows]


@app.get("/students/{student_id}")
def get_student(student_id: str):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM students WHERE student_id = ?",
            (student_id,)
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Student not found")

    return dict(row)


@app.put("/students/{student_id}")
def update_student(student_id: str, student: StudentUpdate):
    changes = student.dict(exclude_unset=True)

    if not changes:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one field to update"
        )

    with get_connection() as conn:
        existing = conn.execute(
            "SELECT * FROM students WHERE student_id = ?",
            (student_id,)
        ).fetchone()

        if existing is None:
            raise HTTPException(
                status_code=404,
                detail="Student not found"
            )

        updated = dict(existing)
        updated.update(changes)

        if not updated.get("email") and not updated.get("phone"):
            raise HTTPException(
                status_code=400,
                detail="Student must have an email or phone number"
            )

        columns = ", ".join(f"{key} = ?" for key in changes)
        values = list(changes.values()) + [student_id]

        conn.execute(
            f"UPDATE students SET {columns} WHERE student_id = ?",
            values
        )

    return {"message": "Student updated successfully"}


@app.delete("/students/{student_id}")
def delete_student(student_id: str):
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM students WHERE student_id = ?",
            (student_id,)
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Student not found"
            )

    return {"message": "Student deleted successfully"}
