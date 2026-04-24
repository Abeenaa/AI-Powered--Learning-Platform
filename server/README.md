# Learning Platform - Backend API

> FastAPI backend for an AI-powered learning platform with roadmap-style course progression.

---

## System Architecture

```
Frontend (React)  ←→  FastAPI Backend  ←→  PostgreSQL Database
                           ↕
                    External Services:
                    - Chapa (Ethiopian payments)
                    - Stripe (International payments)
                    - WebSocket (Real-time chat)
```

**Folder Structure:**
```
server/
├── app/
│   ├── models/      # Database tables (SQLAlchemy)
│   ├── schemas/     # Request/Response validation (Pydantic)
│   ├── routes/      # API endpoints (FastAPI routers)
│   ├── services/    # Business logic (payments, AI, chat)
│   └── utils/       # Helpers (JWT, password hashing)
├── alembic/         # Database migrations
└── requirements.txt
```

---

## Quick Start for Frontend Developer

### Base URL
```
http://localhost:8000
```

### Interactive API Docs
Once the server is running, visit:
- **Swagger UI** (try endpoints directly): http://localhost:8000/docs
- **ReDoc** (clean documentation): http://localhost:8000/redoc

---

## Authentication

All protected endpoints require a Bearer token in the Authorization header.

**How to get a token:**
1. Register or login
2. Copy the `access_token` from the response
3. Add to every request header: `Authorization: Bearer YOUR_TOKEN`

---

## API Endpoints

### Auth
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Create new account | No |
| POST | `/auth/login` | Login and get token | No |
| GET | `/auth/me` | Get current user info | Yes |

**Register body:**
```json
{
  "email": "user@example.com",
  "full_name": "John Doe",
  "password": "password123",
  "role": "student",
  "country": "Ethiopia"
}
```

**Login body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response includes:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": { "id": 1, "email": "...", "full_name": "...", "role": "student" }
}
```

---

### Courses (Public - No Auth Needed)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/courses` | List all courses |
| GET | `/courses/{id}` | Get course details |
| GET | `/courses/{id}/roadmap` | Get lesson roadmap with locked/unlocked status |

**Roadmap response:**
```json
{
  "course_id": 1,
  "course_title": "Python Basics",
  "total_lessons": 5,
  "completed_lessons": 2,
  "progress_percentage": 40.0,
  "lessons": [
    { "id": 1, "title": "Intro", "order": 1, "locked": false, "completed": true },
    { "id": 2, "title": "Variables", "order": 2, "locked": false, "completed": false },
    { "id": 3, "title": "Loops", "order": 3, "locked": true, "completed": false }
  ]
}
```

### Courses (Teacher Only)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/courses` | Create a course |
| PUT | `/courses/{id}` | Update a course |
| DELETE | `/courses/{id}` | Delete a course |
| POST | `/courses/{id}/lessons` | Add lesson to course |
| PUT | `/courses/lessons/{id}` | Update a lesson |
| DELETE | `/courses/lessons/{id}` | Delete a lesson |

---

### Enrollment & Progress
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/enrollments` | Enroll in a course | Yes |
| GET | `/enrollments/my` | Get my enrolled courses with progress | Yes |
| GET | `/enrollments/{id}/progress` | Get lesson progress for enrollment | Yes |
| POST | `/enrollments/progress` | Mark a lesson as complete | Yes |

**Enroll body:**
```json
{ "course_id": 1 }
```

**Mark lesson complete body:**
```json
{
  "enrollment_id": 1,
  "lesson_id": 2
}
```

---

### Payments
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/payments/initiate` | Start payment (auto-detects Chapa/Stripe) | Yes |
| GET | `/payments/chapa/verify/{tx_ref}` | Verify Chapa payment | No |
| POST | `/payments/stripe/webhook` | Stripe webhook (called by Stripe) | No |
| GET | `/payments/{id}/status` | Check payment status | Yes |
| GET | `/payments/history` | Get payment history | Yes |

**Payment flow:**
1. Call `POST /payments/initiate` with `{ "course_id": 1 }`
2. Get back `checkout_url`
3. Redirect user to `checkout_url`
4. After payment, Chapa/Stripe confirms automatically

**Country detection:**
- User with `country: "Ethiopia"` → Chapa (ETB)
- All other countries → Stripe (USD)

---

### Chat
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/chat/conversations` | List all conversations | Yes |
| GET | `/chat/{user_id}/messages` | Get messages with a user | Yes |
| POST | `/chat/send` | Send a message (REST) | Yes |
| WebSocket | `/chat/ws/{receiver_id}?token=JWT` | Real-time chat | Token in URL |

**Send message body:**
```json
{
  "receiver_id": 2,
  "message": "Hello!",
  "file_url": null
}
```

**WebSocket connection:**
```javascript
const ws = new WebSocket(`ws://localhost:8000/chat/ws/2?token=${yourToken}`)
ws.send(JSON.stringify({ message: "Hello!" }))
ws.onmessage = (e) => console.log(JSON.parse(e.data))
```

---

### AI Features
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/ai/recommendations` | Get personalized course recommendations | Yes |
| GET | `/ai/next-lesson?course_id=1` | Get next lesson suggestion | Yes |

---

### User Profile
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/users/profile` | Get current user profile | Yes |
| PUT | `/users/profile` | Update profile | Yes |
| GET | `/users/stats` | Get learning statistics | Yes |
| GET | `/users/my-courses` | Get teacher's created courses (Teacher only) | Yes |
| GET | `/users/my-courses/{id}/students` | Get students in a course (Teacher only) | Yes |

**Update profile body:**
```json
{
  "full_name": "New Name",
  "country": "Ethiopia",
  "profile_picture": "https://..."
}
```

**Stats response:**
```json
{
  "enrolled_courses": 3,
  "completed_lessons": 10,
  "total_lessons": 25,
  "overall_progress": 40.0,
  "courses_created": 0
}
```

---

## Error Responses

All errors follow this format:
```json
{ "detail": "Error message here" }
```

Common status codes:
- `400` - Bad request (e.g., already enrolled)
- `401` - Not authenticated (missing or expired token)
- `403` - Forbidden (wrong role, e.g., student trying teacher action)
- `404` - Not found
- `500` - Server error

---

## Setup (For Backend Dev)

```bash
cd server
python -m venv venv
source venv/Scripts/activate  # Windows Git Bash
pip install -r requirements.txt
cp .env.example .env           # Fill in your values
alembic upgrade head           # Create database tables
uvicorn app.main:app --reload  # Start server
```

---

## Tech Stack
- **FastAPI** - Web framework
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM
- **JWT** - Authentication
- **Chapa** - Ethiopian payments
- **Stripe** - International payments
- **WebSockets** - Real-time chat

---

## Architecture Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Framework | FastAPI | Fast, async, auto-generates API docs |
| Database | PostgreSQL | Reliable relational DB for structured learning data |
| ORM | SQLAlchemy | Powerful Python ORM with migration support |
| Auth | JWT tokens | Stateless, works well with React frontend |
| Payments | Chapa + Stripe | Chapa for Ethiopia (ETB), Stripe for international (USD) |
| Real-time | WebSockets | Native FastAPI support, no extra infrastructure needed |
| AI | Smart algorithm | Progress-based recommendations without external API costs |

---

## Team

- **Backend**: FastAPI (this repo - `server/` folder)
- **Frontend**: React (same repo - `src/` folder)
- **Integration branch**: `develop`
- **Production branch**: `main`
