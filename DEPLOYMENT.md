# DeskPilot AI Deployment Guide

This guide explains how to restart, run, and deploy the DeskPilot AI support automation project.

## Local Deployment

### 1. Start MySQL

Make sure MySQL Server is running on your system.

Then create the database and tables:

```powershell
mysql -u root -p < database.sql
```

To check stored data:

```powershell
mysql -u root -p
```

Inside MySQL:

```sql
USE deskpilot_ai;
SHOW TABLES;
SELECT * FROM companies;
SELECT * FROM tickets;
```

### 2. Set Environment Variables

PowerShell:

```powershell
$env:MYSQL_HOST="localhost"
$env:MYSQL_PORT="3306"
$env:MYSQL_USER="root"
$env:MYSQL_PASSWORD="your_mysql_password"
$env:MYSQL_DATABASE="deskpilot_ai"
$env:N8N_WEBHOOK_URL="http://localhost:5678/webhook/deskpilot"
```

### 3. Start n8n

```powershell
npx n8n
```

Open:

```text
http://localhost:5678
```

Import the workflow:

```text
n8n_workflow_FINAL_WITH_RANDOM_TICKET_ID.json
```

Configure these credentials in n8n:

- MySQL credential
- Gmail SMTP credential

### 4. Start Flask

In a new terminal:

```powershell
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## GitHub Deployment Preparation

Before pushing to GitHub:

1. Confirm `.env` is not committed.
2. Confirm real passwords are not inside source code.
3. Commit only clean project files.
4. Add screenshots or diagrams if needed for your project report.

## Production Deployment Options

DeskPilot AI uses three services, so production deployment should host each part properly.

| Component | Recommended Deployment |
| --- | --- |
| Flask App | Render, Railway, Fly.io, PythonAnywhere, or VPS |
| MySQL | Railway MySQL, PlanetScale, Aiven, AWS RDS, or VPS MySQL |
| n8n | n8n Cloud, Railway, Render, Docker VPS, or local server |
| Email | Gmail SMTP App Password or production SMTP provider |

## Production Environment Variables

Set these variables in your hosting platform:

```text
MYSQL_HOST=your_database_host
MYSQL_PORT=3306
MYSQL_USER=your_database_user
MYSQL_PASSWORD=your_database_password
MYSQL_DATABASE=deskpilot_ai
N8N_WEBHOOK_URL=https://your-n8n-domain/webhook/deskpilot
```

## Production Workflow

1. Deploy MySQL and run `database.sql`.
2. Deploy or configure n8n.
3. Import the DeskPilot workflow JSON into n8n.
4. Configure MySQL and Gmail SMTP credentials in n8n.
5. Deploy the Flask app.
6. Add the production n8n webhook URL in Flask environment variables.
7. Submit a test ticket from the web portal.
8. Verify ticket insertion in MySQL.
9. Verify confirmation email is received.

## Common Issues

### MySQL Password Error in PowerShell

Use quotes:

```powershell
$env:MYSQL_PASSWORD="your_password"
```

### n8n Webhook Not Found

Make sure the workflow is active and the webhook path is:

```text
deskpilot
```

### Gmail SMTP Error

Use a Gmail App Password. Do not use the normal Gmail login password.

### Flask Cannot Connect to MySQL

Check:

- MySQL Server is running
- Database name is `deskpilot_ai`
- Environment variables are set correctly
- MySQL user has permission to insert and select data
