# CivicConnect 🏙️
### Community Issue Tracker | Smart India Hackathon 2025

> Cleared the institute-level internal round and shortlisted for Smart India Hackathon 2025 at KJ Somaiya College of Engineering.

CivicConnect is a civic issue reporting and tracking platform that bridges the gap between citizens and government authorities. Citizens can report local issues like potholes, broken streetlights, and garbage dumps — and track them in real time until resolved.

---

## Features

### For Citizens
- **Report Issues** — Submit complaints with location tagging, photos, and descriptions
- **Real-Time Tracking** — Track status from `Reported → Verified → In Progress → Resolved`
- **Community Validation** — Upvote existing issues to strengthen their credibility
- **Interactive Map** — View all reported issues in your area on a community map
- **Gamification** — Earn points for reporting and upvoting; compete on the leaderboard

### For Government Authorities (Admin)
- **Admin Dashboard** — View and manage all reported issues in one place
- **Status Management** — Update issue status with proof-based resolution
- **Analytics** — Track open vs resolved issues and active users
- **Duplicate Detection** — Issues within 100m of the same category are flagged automatically

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML, CSS, JavaScript (Single Page Application) |
| Backend | Python, Flask, Flask-CORS |
| Database | PostgreSQL (Supabase) |
| Deployment | Vercel (frontend) + Supabase (database) |
| APIs | OpenStreetMap Nominatim (reverse geocoding) |

---

## Getting Started

### Prerequisites
- Python 3.x
- A PostgreSQL database (Supabase free tier works)

### Setup

1. Clone the repo
```bash
git clone https://github.com/atharva7406/connect.git
cd connect
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory
```
DATABASE_URL=postgresql://your-connection-string-here
```

4. Run the app
```bash
python app.py
```

5. Open `http://localhost:5000` in your browser

### Demo Credentials
| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| User | Register a new account | — |

---

## Project Structure

```
connect/
├── app.py          # Flask backend — API routes, DB logic
├── index.html      # Frontend — single page app (HTML/CSS/JS)
└── requirements.txt
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/users/register` | Register new user |
| POST | `/api/users/login` | User/Admin login |
| GET | `/api/issues` | Get all issues (with filters) |
| POST | `/api/issues` | Report a new issue |
| POST | `/api/issues/:id/upvote` | Upvote an issue |
| PUT | `/api/issues/:id/status` | Update issue status (Admin) |
| GET | `/api/users/leaderboard` | Get points leaderboard |
| GET | `/api/admin/stats` | Get admin dashboard stats |

---

## How It Works

1. Citizens register and log in
2. They report an issue with a title, category, location, and description
3. The backend checks for duplicate issues within 100 metres of the same category — if found, the user is prompted to upvote the existing one instead
4. Admins review issues and update their status
5. When an issue is resolved, the reporter earns bonus points
6. All users compete on a leaderboard based on points earned

---

## Built With ❤️ for SIH 2025
Team project built for Smart India Hackathon 2025 — Problem Statement focused on civic issue reporting and government accountability.
