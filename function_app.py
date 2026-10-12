"""
Module: function_app.py
Description: Azure Functions entry point for the Galaxy Telecom IT Service Desk API.
             Wraps the FastAPI application using the Azure Functions ASGI adapter
             so the API can run as an HTTP-triggered Azure Function.
             This file is the bridge between Azure Functions runtime and FastAPI.
             No business logic lives here — all routing and logic stays in main.py.
Author: Gayatri Anne
Created: October 2026
"""

# ============================================================
# IMPORTS
# ============================================================
import azure.functions as func
from azure.functions import AsgiMiddleware
from main import app

# ============================================================
# ASGI ADAPTER
# ============================================================
# Azure Functions does not natively run ASGI frameworks like FastAPI.
# AsgiMiddleware bridges the gap — it wraps the FastAPI app instance
# and translates Azure Functions HTTP trigger events into ASGI-compatible
# requests that FastAPI can handle.
#
# How it works:
#   1. An HTTP request arrives at the Azure Functions endpoint
#   2. Azure Functions runtime triggers the http_app function below
#   3. AsgiMiddleware translates the trigger event into an ASGI request
#   4. FastAPI processes it through its normal routing logic
#   5. The response is translated back and returned by Azure Functions
#
# This pattern means the FastAPI code (main.py, routes, models) does
# not need any Azure-specific changes — it runs identically locally
# via uvicorn and in production via this adapter.
# ============================================================
app_func = func.FunctionApp()

@app_func.function_name("HttpTrigger")
@app_func.route(route="{*route}", auth_level=func.AuthLevel.FUNCTION)
async def http_app(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    return await AsgiMiddleware(app).handle_async(req, context)