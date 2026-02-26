#!/bin/bash

# Variables
DB_USER="bkdsDev"
DB_PASSWORD="your_password" # Replace with a secure password
DB_NAME="your_database" # Replace with your database name

# Login to PostgreSQL
sudo -u postgres psql -c "

# Create User
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';

# Create Database
CREATE DATABASE $DB_NAME;

# Connect to the Database
\c $DB_NAME

# Create Schemas
CREATE SCHEMA staging;
CREATE SCHEMA warehouse;
CREATE SCHEMA reporting;
CREATE SCHEMA views;
CREATE SCHEMA wip;
CREATE SCHEMA dev;

# Grant Permissions
GRANT ALL PRIVILEGES ON SCHEMA staging, warehouse, reporting, views, wip, dev TO $DB_USER;
"
