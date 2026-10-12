# Galaxy Telecom IT Service Desk Agent

An AI-powered IT support agent built with Microsoft Copilot Studio, Azure Functions, Azure SQL, and Microsoft Graph API. Employees interact with the agent in Microsoft Teams to troubleshoot IT issues and raise support tickets -- no forms, no portals, just a conversation.

## Architecture

```
Employee (Teams)
    |
Copilot Studio Agent (Standard Harness)
    | Tools (Custom Connector)
Azure Functions (FastAPI, Flex Consumption, Python 3.12)
    |                          |
Azure SQL Database      Microsoft Graph API
(tickets table)         (confirmation email)
    |
Managed Identity (no passwords anywhere)
```

## Features

- Troubleshoot IT issues using SharePoint knowledge base
- Raise support tickets via natural language conversation
- Automatic confirmation email via Microsoft Graph API using Managed Identity
- Check status of a specific ticket by ticket number
- List all open and in-progress tickets
- Entra-only authentication on Azure SQL -- no SQL passwords stored anywhere
- FUNCTION auth level on Azure Functions API

## Tech Stack

| Layer | Technology |
|---|---|
| AI Agent | Microsoft Copilot Studio (Standard Harness) |
| API | FastAPI on Azure Functions Flex Consumption |
| Database | Azure SQL (Entra-only auth, Managed Identity) |
| Email | Microsoft Graph API (Mail.Send via Managed Identity) |
| Connector | Power Platform Custom Connector (API Key auth) |
| Language | Python 3.12 |
| Auth | Microsoft Entra ID, DefaultAzureCredential |

## Project Structure

```
galaxy-telecom-servicedesk/
├── main.py                 # FastAPI app entry point
├── function_app.py         # Azure Functions ASGI wrapper
├── config.py               # Environment variable loader
├── database.py             # Azure SQL connection via Managed Identity
├── models.py               # Pydantic request/response models
├── routes/
│   └── tickets.py          # Ticket endpoints (raise, status, list)
├── requirements.txt        # Python dependencies
├── local.settings.json     # Local dev settings (not committed)
└── .env                    # Local env vars (not committed)
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /tickets | Raise a new support ticket |
| GET | /tickets | List open and in-progress tickets for an employee |
| GET | /tickets/{ticket_number} | Get status of a specific ticket |

## Local Development

### Prerequisites

- Python 3.12
- Azure Functions Core Tools v4
- ODBC Driver 18 for SQL Server
- Azure CLI (logged in with `az login`)

### Setup

```bash
# Clone the repo
git clone https://github.com/gayatrianne/galaxy-telecom-servicedesk.git
cd galaxy-telecom-servicedesk

# Install dependencies
pip install -r requirements.txt

# Copy and fill in environment variables
cp .env.example .env

# Run locally
uvicorn main:app --reload
```

Swagger UI available at: `http://localhost:8000/api/docs`

### Environment Variables

```
SQL_SERVER=<your-azure-sql-server>.database.windows.net
SQL_DATABASE=<your-database-name>
API_TITLE=Galaxy Telecom IT Service Desk API
API_DESCRIPTION=REST API for the IT Support Agent
API_VERSION=1.0.0
POWER_AUTOMATE_URL=<not required -- email handled via Graph API>
```

## Azure SQL Schema

```sql
CREATE TABLE tickets (
    ticket_id     INT IDENTITY(1,1) PRIMARY KEY,
    ticket_number AS ('INC-' + RIGHT('0000' + CAST(ticket_id AS VARCHAR), 4)) PERSISTED,
    issue_key     VARCHAR(50)   NOT NULL,
    title         VARCHAR(255)  NOT NULL,
    category      VARCHAR(50)   NOT NULL,
    priority      VARCHAR(20)   NOT NULL,
    tags          VARCHAR(255),
    description   NVARCHAR(MAX) NOT NULL,
    notes         NVARCHAR(MAX),
    employee_email VARCHAR(255) NOT NULL,
    employee_name  VARCHAR(255) NOT NULL,
    status        VARCHAR(20)   NOT NULL DEFAULT 'Open',
    created_at    DATETIME2     NOT NULL DEFAULT SYSDATETIME(),
    updated_at    DATETIME2     NOT NULL DEFAULT SYSDATETIME()
);
```

## Deployment

```bash
# Deploy to Azure Functions
func azure functionapp publish galaxy-telecom-api
```

## Key Design Decisions

**Managed Identity for all Azure service auth** -- DefaultAzureCredential works locally via `az login` and automatically uses Managed Identity on Azure Functions. No passwords or keys stored anywhere.

**Email via Microsoft Graph API** -- Confirmation emails are sent directly from FastAPI after ticket insert using a Graph API token obtained from Managed Identity. This eliminates field mapping ambiguity that occurs when routing email through Copilot Studio tools.

**FUNCTION auth level** -- The Azure Functions endpoint requires an API key. The key is stored in the Power Platform Custom Connector connection, not exposed to end users.

**Entra-only Azure SQL** -- No SQL authentication enabled on the server. Access is granted only via `CREATE USER [galaxy-telecom-api] FROM EXTERNAL PROVIDER` with `db_datareader` and `db_datawriter` roles.

## Author

Gayatri Anne -- AI and Cloud Architect | 18+ Years Enterprise IT
