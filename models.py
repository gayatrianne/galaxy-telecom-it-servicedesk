"""
Module: models.py
Description: Pydantic request and response models for the Galaxy Telecom
             IT Service Desk API. All incoming request bodies and outgoing
             response shapes are defined here so they are consistent across
             all route handlers and easy to update in one place.
Author: Gayatri Anne
Created: October 2026
"""

# ============================================================
# IMPORTS
# ============================================================
from pydantic import BaseModel
from typing import Optional

# ============================================================
# REQUEST MODELS
# ============================================================
# Pydantic models define the expected JSON body for each request.
# FastAPI validates incoming requests against these models
# automatically and returns a 422 Unprocessable Entity error
# if required fields are missing or of the wrong type.
#
# Fields typed as Optional[str] with a None default are not
# required in the request body — the API will accept the
# request without them and store NULL in the database.
# ============================================================

class RaiseTicketRequest(BaseModel):
    """
    Request body for POST /tickets.
    Sent by the Copilot Studio agent when an employee confirms
    they want to raise a support ticket.
    """
    issue_key:      str
    title:          str
    category:       str
    priority:       str
    tags:           Optional[str] = None
    description:    str
    notes:          Optional[str] = None
    employee_email: str
    employee_name:  Optional[str] = None


# ============================================================
# RESPONSE MODELS
# ============================================================
# Response models define the shape of the JSON returned by
# each endpoint. Explicit response models make the API
# self-documenting in the Swagger UI and ensure the Custom
# Connector definition in Power Platform has accurate output
# schemas for the agent to map variables from.
# ============================================================

class RaiseTicketResponse(BaseModel):
    """
    Response body for POST /tickets.
    Returns the generated ticket number so the agent can
    confirm it to the employee in the Teams conversation.
    """
    ticket_id:     int
    ticket_number: str
    status:        str
    message:       str


class TicketStatusResponse(BaseModel):
    """
    Response body for GET /tickets/{ticket_number}.
    Returns current status and timestamps for a single ticket.
    """
    ticket_number: str
    title:         str
    category:      str
    priority:      str
    status:        str
    created_at:    str
    updated_at:    str


class TicketSummary(BaseModel):
    """
    Single ticket entry used inside the list response.
    """
    ticket_number: str
    title:         str
    category:      str
    priority:      str
    status:        str
    created_at:    str


class ListTicketsResponse(BaseModel):
    """
    Response body for GET /tickets.
    Returns all open tickets for the employee.
    """
    tickets: list[TicketSummary]
    message: Optional[str] = None