"""
Module: config.py
Description: Central configuration for the Galaxy Telecom IT Service Desk API.
             All environment-specific values are loaded from the .env file
             so nothing sensitive is hardcoded or committed to GitHub.
             In production, the same variable names are set in Azure Functions
             Application Settings — python-dotenv is ignored there since the
             values are already in the environment.
Author: Gayatri Anne
Created: October 2026
"""

# ============================================================
# IMPORTS
# ============================================================
import os
from dotenv import load_dotenv

# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================
# Reads key=value pairs from the .env file in the project root
# and injects them into os.environ so they are available
# throughout the application via os.getenv().
#
# load_dotenv() does nothing if the variables are already set
# in the environment — so this is safe to leave in production
# code. Azure Functions Application Settings take precedence.
#
# The .env file must be added to .gitignore before pushing
# to GitHub so credentials are never committed to source control.
# ============================================================
load_dotenv()

# ============================================================
# DATABASE CONFIGURATION
# ============================================================
SERVER   = os.getenv("SQL_SERVER")
DATABASE = os.getenv("SQL_DATABASE")

# ============================================================
# API METADATA
# ============================================================
# Used by FastAPI to populate the Swagger UI (/docs) and
# OpenAPI spec (/openapi.json), which is also the source
# for generating the Power Platform Custom Connector definition.
# ============================================================
API_TITLE       = os.getenv("API_TITLE")
API_DESCRIPTION = os.getenv("API_DESCRIPTION")
API_VERSION     = os.getenv("API_VERSION")
POWER_AUTOMATE_URL = os.getenv("POWER_AUTOMATE_URL")