"""
Module: database.py
Description: Database connection handler for the Galaxy Telecom IT Service Desk API.
             Establishes a connection to Azure SQL using Managed Identity
             (DefaultAzureCredential) — no passwords or connection strings stored.
             This module is imported by route handlers whenever a database
             operation is needed.
Author: Gayatri Anne
Created: October 2026
"""

# ============================================================
# IMPORTS
# ============================================================
import struct
import pyodbc
from azure.identity import DefaultAzureCredential
from config import SERVER, DATABASE

# ============================================================
# DATABASE CONNECTION
# ============================================================
# Connects to Azure SQL using a short-lived Entra ID token
# rather than a SQL username and password.
#
# How it works:
#   1. DefaultAzureCredential fetches a token from Entra ID
#      Locally: uses your active az login session
#      On Azure Functions: uses the Function app Managed Identity
#   2. The token is encoded as UTF-16-LE and packed into a
#      binary struct — this is the format pyodbc expects for
#      token-based authentication (ODBC attribute 1256)
#   3. pyodbc opens the connection using that token instead
#      of a username or password
#
# Production note:
#   The Managed Identity of the Azure Functions app must be
#   granted db_datareader and db_datawriter roles on the database.
#   This is done once in Azure SQL after the Functions app is created.
#   No credentials are stored anywhere — access is identity-based.
# ============================================================
def get_connection():
    credential    = DefaultAzureCredential()
    token         = credential.get_token("https://database.windows.net/.default")
    token_bytes   = token.token.encode("UTF-16-LE")
    token_struct  = struct.pack(f"<I{len(token_bytes)}s", len(token_bytes), token_bytes)
    conn = pyodbc.connect(
        f"Driver={{ODBC Driver 18 for SQL Server}};"
        f"Server={SERVER};"
        f"Database={DATABASE};",
        attrs_before={1256: token_struct}
    )
    return conn