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

## Recommended Free Deployment Path

For the easiest live demo, use:

1. Render for the Flask web app
2. Railway or another hosted MySQL provider for the MySQL database
3. n8n Cloud trial, Railway, or a VPS-hosted n8n instance for the workflow
4. Gmail App Password for SMTP email sending

Vercel is excellent for static and serverless frontend projects, but this project is a Flask backend connected to MySQL and n8n. Render is a better fit because it can run the Flask app using Gunicorn as a web service.

## Deploy Flask App on Render

Render can deploy directly from your GitHub repository.

1. Go to:

```text
https://render.com
```

2. Sign in with GitHub.

3. Click:

```text
New > Web Service
```

4. Select your repository:

```text
Pratham2801/DeskPiolt-AI
```

5. Use these settings:

| Setting | Value |
| --- | --- |
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app` |
| Plan | Free |

This repository also includes `render.yaml`, so Render can detect most deployment settings automatically.

## Deploy MySQL

Use a hosted MySQL provider such as Railway.

1. Create a new MySQL database.
2. Copy the database host, port, user, password, and database name.
3. Run the SQL from `database.sql` inside the hosted MySQL console.
4. Add the same database values in Render environment variables.

Required Render environment variables:

```text
MYSQL_HOST=your_mysql_host
MYSQL_PORT=3306
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=deskpilot_ai
N8N_WEBHOOK_URL=https://your-n8n-domain/webhook/deskpilot
```

## Deploy n8n

You need a public n8n URL because the live Flask app cannot call `localhost`.

Options:

1. n8n Cloud trial
2. Railway deployment
3. Render Docker deployment
4. VPS deployment using Docker

After deployment:

1. Import `n8n_workflow.json`.
2. Configure MySQL credentials.
3. Configure Gmail SMTP credentials.
4. Activate the workflow.
5. Copy the production webhook URL.
6. Add that URL as `N8N_WEBHOOK_URL` in Render.

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
