-- PostgreSQL initialization script for CVProject
-- This script runs when the PostgreSQL container is first created

-- Create database if it doesn't exist
SELECT 'CREATE DATABASE cvproject'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'cvproject')\gexec

-- Connect to the database
\c cvproject;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create user if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'cvproject_user') THEN
        CREATE ROLE cvproject_user WITH LOGIN PASSWORD 'cvproject_password';
    END IF;
END
$$;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE cvproject TO cvproject_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO cvproject_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO cvproject_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO cvproject_user;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO cvproject_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO cvproject_user;

-- Create indexes for better performance (will be created by Django migrations)
-- These are just examples of what Django will create

-- Log successful initialization
-- Note: pg_stat_statements_info requires pg_stat_statements extension to be enabled
-- This is just a placeholder for successful initialization
