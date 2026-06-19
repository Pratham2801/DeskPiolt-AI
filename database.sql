CREATE DATABASE IF NOT EXISTS deskpilot_ai;

USE deskpilot_ai;

CREATE TABLE IF NOT EXISTS companies (
id INT AUTO_INCREMENT PRIMARY KEY,
name VARCHAR(255) NOT NULL,
slug VARCHAR(120) NOT NULL UNIQUE,
ticket_table VARCHAR(128) NOT NULL UNIQUE,
active BOOLEAN DEFAULT TRUE,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tickets (
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
);

CREATE TABLE IF NOT EXISTS tickets_amazon (
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
);

CREATE TABLE IF NOT EXISTS tickets_flipkart (
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
);

CREATE TABLE IF NOT EXISTS tickets_myntra (
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
);

INSERT INTO companies (name, slug, ticket_table)
VALUES
('Amazon', 'amazon', 'tickets_amazon'),
('Flipkart', 'flipkart', 'tickets_flipkart'),
('Myntra', 'myntra', 'tickets_myntra')
ON DUPLICATE KEY UPDATE
name = VALUES(name),
ticket_table = VALUES(ticket_table),
active = TRUE;
