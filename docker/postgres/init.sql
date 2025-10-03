-- PostgreSQL initialization script for CVProject
-- This script runs when the PostgreSQL container is first created

-- Create database if it doesn't exist (handled by POSTGRES_DB env var)
-- CREATE DATABASE cvproject;

-- Create user if it doesn't exist (handled by POSTGRES_USER env var)
-- CREATE USER cvproject_user WITH PASSWORD 'cvproject_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE cvproject TO cvproject_user;

-- Set timezone
SET timezone = 'UTC';

-- Create extensions that might be useful
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'CVProject PostgreSQL database initialized successfully';
END $$;
