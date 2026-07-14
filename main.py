import os
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database import engine, get_db, Base
from models import Ticket, Note
from schemas import (
    TicketCreate, TicketUpdate, TicketResponse,
    TicketListItem
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ticket-CRM")

app.mount("/static", StaticFiles(directory="static"), name="static")


def generate_ticket_id(db: Session) -> str:
    count = db.query(Ticket).count()
    return f"TKT-{count + 1:03d}"


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/tickets")
def create_ticket(payload: TicketCreate, db: Session = Depends(get_db)):
    ticket_id = generate_ticket_id(db)
    ticket = Ticket(
        ticket_id=ticket_id,
        customer_name=payload.customer_name,
        customer_email=payload.customer_email,
        subject=payload.subject,
        description=payload.description,
        status="Open",
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return {"ticket_id": ticket.ticket_id, "created_at": ticket.created_at.isoformat()}


@app.get("/api/tickets")
def list_tickets(
    status: str = Query(None),
    search: str = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Ticket)
    if status and status.lower() != "all":
        query = query.filter(Ticket.status == status)
    if search:
        term = f"%{search}%"
        query = query.filter(
            or_(
                Ticket.customer_name.ilike(term),
                Ticket.ticket_id.ilike(term),
                Ticket.customer_email.ilike(term),
                Ticket.subject.ilike(term),
                Ticket.description.ilike(term),
            )
        )
    tickets = query.order_by(Ticket.created_at.desc()).all()
    return [
        TicketListItem(
            ticket_id=t.ticket_id,
            customer_name=t.customer_name,
            subject=t.subject,
            status=t.status,
            created_at=t.created_at,
        )
        for t in tickets
    ]


@app.get("/api/tickets/{ticket_id}")
def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    notes = db.query(Note).filter(Note.ticket_id == ticket_id).order_by(Note.created_at.desc()).all()
    return TicketResponse(
        ticket_id=ticket.ticket_id,
        customer_name=ticket.customer_name,
        customer_email=ticket.customer_email,
        subject=ticket.subject,
        description=ticket.description,
        status=ticket.status,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        notes=[{"id": n.id, "note_text": n.note_text, "created_at": n.created_at} for n in notes],
    )


@app.put("/api/tickets/{ticket_id}")
def update_ticket(ticket_id: str, payload: TicketUpdate, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if payload.status:
        ticket.status = payload.status
    if payload.notes:
        note = Note(ticket_id=ticket_id, note_text=payload.notes)
        db.add(note)
    db.commit()
    db.refresh(ticket)
    return {"success": True, "updated_at": ticket.updated_at.isoformat()}


@app.get("/{path:path}")
def serve_frontend(path: str):
    if path == "" or path == "/":
        path = "index.html"
    file_path = os.path.join("static", path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    return FileResponse("static/index.html")
