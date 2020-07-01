-- Example database upgrade script for Crew DB
-- SQL is written with PostgreSQL syntax

DROP TABLE users;

UPDATE settings
SET version = 2;