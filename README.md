# Visitor Entry System

A complete solution for managing visitor registrations, security, and gate passes in your facility.

## Features

- **Visitor Management** — Register visitors, track entry/exit times, maintain detailed records
- **Gate Pass Generation** — Create and manage gate passes with expiration dates and status tracking
- **Dashboard Analytics** — View real-time statistics and recent visitor activity
- **Role-Based Access Control** — Three roles: Admin (full access), Staff (add/exit/pass), Student (read-only)

## Quick Start

```bash
cd frontend
pip install -r requirements.txt
python app.py
```

Visit `http://127.0.0.1:5000`

## Default Users

| Username | Password   | Role   |
|----------|------------|--------|
| admin    | admin123   | admin  |
| staff    | staff123   | staff  |
| student  | student123 | student|

## Project Structure

```
frontend/
  app.py           # Flask backend with SQLite
  requirements.txt # Python dependencies
  style.css        # CSS styles
  script.js        # Shared JavaScript utilities
  templates/
    index.html     # Landing page
    login.html     # Login page
    signup.html    # Registration page
    dashboard.html # Dashboard with stats
    visitor.html   # Visitor management
    gatepass.html  # Gate pass management
```
