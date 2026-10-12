"""
Module: main.py
Description: Entry point for the Galaxy Telecom IT Service Desk API.
             Initialises the FastAPI application, registers all route
             modules, and exposes the app instance for Azure Functions
             ASGI adapter and local uvicorn server.
Author: Gayatri Anne
Created: October 2026
"""

# ============================================================
# IMPORTS
# ============================================================
from fastapi import FastAPI
from config import API_TITLE, API_DESCRIPTION, API_VERSION
from routes.tickets import router as tickets_router

# ============================================================
# APPLICATION INITIALISATION
# ============================================================
# Creates the FastAPI app instance with metadata pulled from
# config.py. This metadata populates the Swagger UI at /docs
# and the OpenAPI spec at /openapi.json.
#
# The OpenAPI spec is also the source used to generate the
# Power Platform Custom Connector definition — keeping the
# title and description accurate here matters for the portfolio.
# ============================================================
app = FastAPI(
    title       = API_TITLE,
    description = API_DESCRIPTION,
    version     = API_VERSION,
    root_path   = "/api"
)

# ============================================================
# ROUTE REGISTRATION
# ============================================================
# Each route module is registered here as a router.
# The tickets router handles all /tickets endpoints.
# Future routers (e.g. graph.py for email notifications)
# are added here without touching any existing code.
# ============================================================
app.include_router(tickets_router)


# ============================================================
# ENTRY POINT (LOCAL TESTING ONLY)
# ============================================================
# Run locally with: uvicorn main:app --reload
# Then open:        http://127.0.0.1:8000/docs
#
# The Swagger UI at /docs lets you test all three endpoints
# interactively in the browser without needing Postman.
#
# On Azure Functions the ASGI adapter handles routing —
# uvicorn is not used in production and this block is ignored.
# ============================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)