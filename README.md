
# Students Database CRUD Application

## Project Overview
This project is a student record management REST API built using Python, FastAPI, and SQLite.

## Features
- Create a student record
- View all student records
- Search students by name or course
- View a student by ID
- Update student details
- Delete a student record
- Validate email and contact information

## Technologies Used
- Python
- FastAPI
- SQLite
- Pydantic

## API Endpoints
| Method | Endpoint | Purpose |
|---|---|---|
| POST | /students | Create student |
| GET | /students | List and filter students |
| GET | /students/{student_id} | Get student |
| PUT | /students/{student_id} | Update student |
| DELETE | /students/{student_id} | Delete student |

## Run Locally
1. Install Python 3.10 or later.
2. Install dependencies using:
   pip install fastapi "uvicorn[standard]" "pydantic<2"
3. Start the API using:
   uvicorn main:app --reload
4. Open http://127.0.0.1:8000/docs to test the API.

## Database
SQLite creates the students.db database automatically when the application starts.
