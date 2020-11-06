-- Example database upgrade script for MemberPort
-- SQL is written with PostgreSQL syntax

INSERT INTO permissions (id, name, description)
VALUES ('00000000-0000-0000-0000-000000000000', 'get_members', 'Get information about other members.');

INSERT INTO permissions (id, name, description)
VALUES ('00000000-0000-0000-0000-000000000001', 'edit_members', 'Edit information about other members.');

INSERT INTO permissions (id, name, description)
VALUES ('00000000-0000-0000-0000-000000000002', 'delete_members', 'Delete other members.');

UPDATE settings
SET version = 3;