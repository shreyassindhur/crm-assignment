# Ticket-CRM

A full-stack customer support ticketing system built with FastAPI, SQLite, and Tailwind CSS. Built by Shreyas Sindhur.

## Tech Stack

- **Backend**: Python + FastAPI
- **Database**: SQLite (via SQLAlchemy)
- **Frontend**: HTML + Tailwind CSS + Vanilla JS
- **Deployment**: Railway.app

## Features

1. **Create Tickets** — Create support tickets with customer info, subject, and description
2. **List Tickets** — Clean table view with ID, customer, subject, status, and date
3. **Search** — Real-time search across names, IDs, emails, subjects, and descriptions
4. **Filter by Status** — Filter tickets by Open, In Progress, or Closed
5. **View & Update Tickets** — Detailed ticket view with status updates and notes

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/tickets` | Create a new ticket |
| GET | `/api/tickets` | List tickets (supports `?status=` and `?search=`) |
| GET | `/api/tickets/{ticket_id}` | Get ticket details with notes |
| PUT | `/api/tickets/{ticket_id}` | Update status and/or add notes |

## Local Development

```bash
# Clone the repo
git clone <repo-url>
cd crm-assignment

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload
```

Open http://localhost:8000 in your browser.

## Deployment

The app is deployed on Railway.app. Push to the `main` branch to trigger auto-deployment.

### Railway Setup

1. Connect your GitHub repo to Railway
2. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. Deploy
