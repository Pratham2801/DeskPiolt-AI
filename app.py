import os
import re

from flask import Flask, jsonify, render_template, request
import mysql.connector
from mysql.connector import Error
import requests


app = Flask(__name__)

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/deskpilot")

ISSUE_TYPES = {
    "login": "Login Issue",
    "payment": "Payment Failure",
    "technical": "Technical / Bug Issue",
    "general": "General Inquiry",
}


def db_config():
    return {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": os.getenv("MYSQL_DATABASE", "deskpilot_ai"),
    }


def get_db_connection():
    return mysql.connector.connect(**db_config())


def slugify_company(name):
    slug = re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_")
    return slug[:80] or "company"


def safe_ticket_table(slug):
    safe_slug = re.sub(r"[^a-z0-9_]", "", slug.lower()).strip("_")
    return f"tickets_{safe_slug[:90]}"


def create_company_ticket_table(cursor, table_name):
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS `{table_name}` (
        id INT AUTO_INCREMENT PRIMARY KEY,
        company_id INT,
        company_name VARCHAR(255),
        email VARCHAR(255),
        issue_type VARCHAR(100),
        issue TEXT,
        intent VARCHAR(100),
        priority VARCHAR(50),
        assigned_team VARCHAR(100),
        sla_hours INT,
        sla_deadline DATETIME,
        escalation BOOLEAN,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


def fetch_company(company_id):
    with get_db_connection() as connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, name, slug, ticket_table
            FROM companies
            WHERE id = %s AND active = TRUE
            """,
            (company_id,),
        )
        return cursor.fetchone()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/companies", methods=["GET"])
def list_companies():
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT id, name, slug, ticket_table, created_at
                FROM companies
                WHERE active = TRUE
                ORDER BY name
                """
            )
            return jsonify({"status": "success", "companies": cursor.fetchall()})
    except Error as exc:
        return jsonify(
            {
                "status": "error",
                "message": "Could not load registered companies. Run database.sql and check MySQL settings.",
                "details": str(exc),
            }
        ), 500


@app.route("/api/companies", methods=["POST"])
def register_company():
    data = request.get_json(silent=True) or request.form
    name = (data.get("name") or "").strip()

    if len(name) < 2:
        return jsonify(
            {
                "status": "error",
                "message": "Company name must be at least 2 characters.",
            }
        ), 400

    base_slug = slugify_company(name)

    try:
        with get_db_connection() as connection:
            cursor = connection.cursor(dictionary=True)

            slug = base_slug
            suffix = 2
            while True:
                cursor.execute("SELECT id FROM companies WHERE slug = %s", (slug,))
                if not cursor.fetchone():
                    break
                slug = f"{base_slug}_{suffix}"
                suffix += 1

            table_name = safe_ticket_table(slug)
            create_company_ticket_table(cursor, table_name)

            cursor.execute(
                """
                INSERT INTO companies (name, slug, ticket_table)
                VALUES (%s, %s, %s)
                """,
                (name, slug, table_name),
            )
            connection.commit()

            return jsonify(
                {
                    "status": "success",
                    "message": f"{name} registered successfully.",
                    "company": {
                        "id": cursor.lastrowid,
                        "name": name,
                        "slug": slug,
                        "ticket_table": table_name,
                    },
                }
            ), 201
    except Error as exc:
        return jsonify(
            {
                "status": "error",
                "message": "Could not register company or create its ticket table.",
                "details": str(exc),
            }
        ), 500


@app.route("/submit-ticket", methods=["POST"])
def submit_ticket():
    data = request.get_json(silent=True) or request.form

    email = (data.get("email") or "").strip()
    issue = (data.get("issue") or "").strip()
    priority = (data.get("priority") or "").strip().lower()
    issue_type = (data.get("issue_type") or "").strip().lower()
    company_id = data.get("company_id")

    if not email or not issue or priority not in {"low", "medium", "high"}:
        return jsonify(
            {
                "status": "error",
                "message": "Email, issue, and a valid priority are required.",
            }
        ), 400

    if issue_type not in ISSUE_TYPES:
        return jsonify(
            {
                "status": "error",
                "message": "Please select a valid issue category.",
            }
        ), 400

    try:
        company_id = int(company_id)
    except (TypeError, ValueError):
        return jsonify(
            {
                "status": "error",
                "message": "Please select a registered company.",
            }
        ), 400

    try:
        company = fetch_company(company_id)
    except Error as exc:
        return jsonify(
            {
                "status": "error",
                "message": "Could not verify selected company.",
                "details": str(exc),
            }
        ), 500

    if not company:
        return jsonify(
            {
                "status": "error",
                "message": "Selected company was not found.",
            }
        ), 404

    payload = {
        "company_id": company["id"],
        "company_name": company["name"],
        "company_slug": company["slug"],
        "ticket_table": company["ticket_table"],
        "email": email,
        "issue_type": issue_type,
        "issue_type_label": ISSUE_TYPES[issue_type],
        "issue": issue,
        "user_priority": priority,
    }

    try:
        response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=20)
        response.raise_for_status()
    except requests.RequestException as exc:
        return jsonify(
            {
                "status": "error",
                "message": "Could not reach DeskPilot automation workflow.",
                "details": str(exc),
            }
        ), 502

    try:
        return jsonify(response.json()), response.status_code
    except ValueError:
        return jsonify(
            {
                "status": "success",
                "message": response.text,
            }
        ), response.status_code


if __name__ == "__main__":
    app.run(debug=True)
