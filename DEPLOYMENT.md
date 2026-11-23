# DeskPilot AI Deployment Guide

This guide covers local setup and the deployment layout for DeskPilot AI. The application consists of three separately configured parts:

1. Flask web application
2. MySQL database
3. n8n automation workflow

The included `render.yaml` configures only the Flask web service. It does not create or host the MySQL database or n8n instance.

## 1. Local setup

### Requirements

- Python 3
- MySQL Server and MySQL command-line client
- Node.js and npm
- n8n
- SMTP account/credentials if email confirmations are to be sent

### Step 1: Install Python dependencies

From the project directory:

```powershell
python -m pip install -r requirements.txt
```

### Step 2: Create the database

Run from PowerShell:

```powershell
cmd /c "mysql -u root -p < database.sql"
```

The SQL file creates the `deskpilot_ai` database, the `companies` table, a generic `tickets` table, and initial ticket tables for Amazon, Flipkart and Myntra.

Check the initial database:

```sql
USE deskpilot_ai;
SHOW TABLES;
SELECT * FROM companies;
```

### Step 3: Configure Flask environment variables

Set the values in the same PowerShell session that will run Flask:

```powershell
$env:MYSQL_HOST = "localhost"
$env:MYSQL_PORT = "3306"
$env:MYSQL_USER = "root"
$env:MYSQL_PASSWORD = "your_mysql_password"
$env:MYSQL_DATABASE = "deskpilot_ai"
$env:N8N_WEBHOOK_URL = "http://localhost:5678/webhook/deskpilot"
```

Use your own database credentials. Do not commit real credentials to Git.

### Step 4: Import and configure the n8n workflow

Start n8n:

```powershell
npx n8n
```

Open `http://localhost:5678` and import:

```text
n8n_workflow.json
```

Configure credentials for these workflow nodes:

- `Execute a SQL query`: MySQL credential pointing to the `deskpilot_ai` database.
- `Send Ticket Confirmation Email`: SMTP credential for the sender account.

The workflow JSON contains credential references; importing it does not automatically configure your credential values. Configure the credentials in your own n8n instance.

The webhook path is `deskpilot` and the method is `POST`. During manual testing, use the webhook test URL while n8n is listening for a test event. For normal active execution, activate the workflow and configure Flask with the production webhook URL shown by n8n. Do not assume the test and production URLs are interchangeable.

### Step 5: Start Flask

In a second PowerShell window, set the same Flask environment variables, then run:

```powershell
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

The `app.py` development entry point uses Flask debug mode. It is intended for local development, not public production hosting.

## 2. Verify ticket storage

Tickets are stored in a separate table for each company. For the seeded companies, inspect them with:

```sql
USE deskpilot_ai;

SELECT * FROM tickets_amazon;
SELECT * FROM tickets_flipkart;
SELECT * FROM tickets_myntra;
```

For a newly registered company, inspect its `ticket_table` value in the `companies` table and query that table.

## 3. Deployment architecture

A hosted deployment needs all three components to communicate:

| Component | Deployment responsibility |
| --- | --- |
| Flask | Public web service running the application |
| MySQL | Reachable database containing the DeskPilot schema |
| n8n | Reachable workflow service with the imported and activated workflow |
| SMTP | Outbound email service configured as an n8n credential |

The Flask service must be able to reach MySQL and the n8n webhook. The n8n service must be able to reach MySQL and the SMTP provider.

Do not use `localhost` for a dependency hosted on a different service. In a hosted environment, `localhost` refers to the container or machine running the current service.

## 4. Deploy the Flask service on Render

The repository includes `render.yaml` with these settings:

| Setting | Configured value |
| --- | --- |
| Service type | Web service |
| Runtime | Python |
| Build command | `pip install -r requirements.txt` |
| Start command | `gunicorn app:app` |

Deployment outline:

1. Push the reviewed project to GitHub.
2. Create a Render Web Service and connect the repository.
3. Allow Render to use `render.yaml`, or enter the build and start commands above.
4. Add the required environment variables in the Render service settings.
5. Deploy and inspect the service logs.

The current `render.yaml` uses `plan: free`. Plan availability, limits, eligibility, and pricing can change. Confirm current terms in Render's documentation before relying on a particular plan.

### Flask environment variables

Set these in the hosting service's environment settings:

```text
MYSQL_HOST=your_database_host
MYSQL_PORT=3306
MYSQL_USER=your_database_user
MYSQL_PASSWORD=your_database_password
MYSQL_DATABASE=deskpilot_ai
N8N_WEBHOOK_URL=https://your-n8n-host/webhook/deskpilot
```

Use the actual values supplied by your database and n8n providers. Keep credentials in the hosting platform's secret/environment settings, not in the repository.

## 5. Provision MySQL

1. Create a MySQL database with a provider that permits connections from the Flask and n8n services.
2. Run the contents of `database.sql` against that database.
3. Create a dedicated database user for the application/workflow.
4. Grant only the database permissions needed for the operations performed by the Flask application and workflow.
5. Configure the database connection in both Flask's environment variables and the n8n MySQL credential.

The n8n workflow inserts ticket records into the company-specific table passed by Flask. Confirm that the database user has the permissions needed for the workflow's insert and select operations, and for company-table creation if company registration is used.

Do not expose the MySQL server publicly without appropriate network restrictions and authentication.

## 6. Deploy n8n

Deploy n8n using a hosting option that supports its runtime and persistent configuration. Options may include a managed n8n service or a suitably configured server/container.

After deployment:

1. Open the n8n editor.
2. Import `n8n_workflow.json`.
3. Configure the MySQL credential.
4. Configure the SMTP credential.
5. Check the webhook node path and method.
6. Activate the workflow.
7. Copy the production webhook URL.
8. Set that URL as `N8N_WEBHOOK_URL` in the Flask hosting environment.
9. Redeploy or restart Flask if the hosting platform requires it to load changed environment variables.

The n8n instance must remain available to the Flask application. Configure persistent storage and backups according to the hosting provider's guidance.

## 7. End-to-end deployment test

After all services are configured:

1. Confirm the Flask service is reachable over HTTPS.
2. Confirm the n8n workflow is active.
3. Submit a test ticket through the portal.
4. Confirm the request reaches the n8n workflow.
5. Confirm the expected company-specific MySQL table receives the ticket.
6. Confirm the returned response is displayed by the Flask portal.
7. If SMTP is configured, confirm the customer email is received.
8. Inspect service logs for errors without exposing secrets.

## 8. Troubleshooting

### Flask cannot connect to MySQL

- Confirm the database host, port, username, password and database name.
- Confirm the database is running and accepts connections from the Flask host.
- Confirm the database user has the required permissions.
- Do not use `localhost` when MySQL is hosted on a separate service.

### n8n webhook not found

- Confirm the workflow is imported.
- Confirm the webhook path is `deskpilot` and the method is `POST`.
- For manual test execution, make sure the workflow is listening for a test event.
- For normal execution, activate the workflow and use its production webhook URL.
- Confirm `N8N_WEBHOOK_URL` matches the intended URL.

### MySQL node fails in n8n

- Confirm the n8n MySQL credential points to the correct database host and schema.
- Confirm network access from n8n to MySQL.
- Confirm the database user has the required permissions.
- Check the table name and workflow execution data.

### SMTP node fails

- Confirm the SMTP host, port, encryption mode, username and password.
- Confirm the SMTP provider permits the configured authentication method.
- Store SMTP credentials in n8n credentials, not in the workflow's code or repository.

### Flask returns an automation error

- Confirm `N8N_WEBHOOK_URL` is reachable from the Flask service.
- Inspect the n8n execution log and Flask service log.
- Check that the workflow completed its SQL and email steps.

## 9. Production security checklist

The current code should receive a security review before public production use:

- Add authentication and authorization to company registration.
- Validate email addresses and enforce reasonable request-size limits.
- Add rate limiting to public endpoints.
- Avoid returning raw database and network exception details to clients.
- Keep Flask debug mode disabled in production; use the included Gunicorn start command.
- Use HTTPS for public traffic.
- Use dedicated, least-privilege database credentials.
- Keep database and SMTP secrets out of source control.
- Review the n8n webhook's exposure and access controls.
- Add backups and monitoring appropriate to the deployment.

This guide describes the deployment configuration present in the repository; it does not certify the application as production-hardened.
