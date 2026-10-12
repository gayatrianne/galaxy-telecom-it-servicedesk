"""
Module: routes/tickets.py
Description: Route handlers for all ticket-related endpoints in the
             Galaxy Telecom IT Service Desk API.
             Handles raising tickets, checking ticket status, and
             listing open tickets for an employee.
             Each endpoint connects to Azure SQL via the shared
             database module and validates input via Pydantic models.
             Email notifications are sent via Microsoft Graph API
             using Managed Identity -- no passwords or keys stored.
Author: Gayatri Anne
Created: October 2026
"""

# ============================================================
# IMPORTS
# ============================================================
import requests
from fastapi import APIRouter, HTTPException
from azure.identity import DefaultAzureCredential
from database import get_connection
from models import (
    RaiseTicketRequest,
    RaiseTicketResponse,
    TicketStatusResponse,
    ListTicketsResponse,
    TicketSummary
)

# ============================================================
# ROUTER
# ============================================================
router = APIRouter(prefix="/tickets", tags=["Tickets"])

# ============================================================
# CONSTANTS
# ============================================================
SENDER_EMAIL  = "GayatriCopilot@copilot054.onmicrosoft.com"
GRAPH_API_URL = "https://graph.microsoft.com/v1.0/users/{}/sendMail".format(SENDER_EMAIL)


# ============================================================
# HELPER: SEND CONFIRMATION EMAIL VIA GRAPH API
# ============================================================
# Uses Managed Identity (DefaultAzureCredential) to obtain a
# Graph API token and sends a confirmation email to the employee.
# Fire-and-forget -- called after ticket insert, errors are
# logged but do not affect the ticket creation response.
# ============================================================
def send_confirmation_email(ticket_number, title, category, priority,
                             description, employee_email, employee_name):
    try:
        # Get token for Graph API using Managed Identity
        credential = DefaultAzureCredential()
        token      = credential.get_token("https://graph.microsoft.com/.default")

        email_body = f"""
        <html><body>
        <p>Dear {employee_name},</p>
        <p>Your IT support ticket has been raised successfully.</p>
        <table border="1" cellpadding="6" cellspacing="0">
            <tr><td><b>Ticket Number</b></td><td>{ticket_number}</td></tr>
            <tr><td><b>Title</b></td><td>{title}</td></tr>
            <tr><td><b>Category</b></td><td>{category}</td></tr>
            <tr><td><b>Priority</b></td><td>{priority}</td></tr>
            <tr><td><b>Description</b></td><td>{description}</td></tr>
            <tr><td><b>Status</b></td><td>Open</td></tr>
        </table>
        <p>Our IT team will be in touch shortly.</p>
        <p>Galaxy Telecom IT Support</p>
        </body></html>
        """

        payload = {
            "message": {
                "subject": f"IT Support Ticket Raised: {ticket_number}",
                "body": {
                    "contentType": "HTML",
                    "content": email_body
                },
                "toRecipients": [
                    {"emailAddress": {"address": employee_email}}
                ]
            },
            "saveToSentItems": "false"
        }

        requests.post(
            GRAPH_API_URL,
            json=payload,
            headers={
                "Authorization": f"Bearer {token.token}",
                "Content-Type":  "application/json"
            },
            timeout=10
        )
    except Exception as email_error:
        print(f"Email notification failed: {email_error}")


# ============================================================
# ENDPOINT 1: RAISE A TICKET
# ============================================================
@router.post("", response_model=RaiseTicketResponse)
def raise_ticket(req: RaiseTicketRequest):
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tickets
                (issue_key, title, category, priority, tags,
                 description, notes, employee_email, employee_name)
            OUTPUT INSERTED.ticket_id, INSERTED.ticket_number
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            req.issue_key, req.title, req.category, req.priority,
            req.tags, req.description, req.notes,
            req.employee_email, req.employee_name
        )
        row = cursor.fetchone()
        conn.commit()
        conn.close()

        # Send confirmation email via Graph API (fire-and-forget)
        send_confirmation_email(
            ticket_number  = row[1],
            title          = req.title,
            category       = req.category,
            priority       = req.priority,
            description    = req.description,
            employee_email = req.employee_email,
            employee_name  = req.employee_name
        )

        return RaiseTicketResponse(
            ticket_id     = row[0],
            ticket_number = row[1],
            status        = "Open",
            message       = f"Ticket {row[1]} raised successfully."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# ENDPOINT 2: CHECK TICKET STATUS
# ============================================================
@router.get("/{ticket_number}", response_model=TicketStatusResponse)
def get_ticket_status(ticket_number: str, employee_email: str):
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ticket_number, title, category, priority,
                   status, created_at, updated_at
            FROM tickets
            WHERE ticket_number  = ?
              AND employee_email = ?
        """, ticket_number, employee_email)
        row = cursor.fetchone()
        conn.close()
        if not row:
            raise HTTPException(status_code=404, detail="Ticket not found.")
        return TicketStatusResponse(
            ticket_number = row[0],
            title         = row[1],
            category      = row[2],
            priority      = row[3],
            status        = row[4],
            created_at    = str(row[5]),
            updated_at    = str(row[6])
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# ENDPOINT 3: LIST MY OPEN TICKETS
# ============================================================
@router.get("", response_model=ListTicketsResponse)
def list_open_tickets(employee_email: str):
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ticket_number, title, category, priority, status, created_at
            FROM tickets
            WHERE employee_email = ?
              AND status IN ('Open', 'In Progress')
            ORDER BY created_at DESC
        """, employee_email)
        rows = cursor.fetchall()
        conn.close()
        if not rows:
            return ListTicketsResponse(
                tickets = [],
                message = "No open tickets found."
            )
        return ListTicketsResponse(
            tickets = [
                TicketSummary(
                    ticket_number = r[0],
                    title         = r[1],
                    category      = r[2],
                    priority      = r[3],
                    status        = r[4],
                    created_at    = str(r[5])
                )
                for r in rows
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))