-- Database structure for Crew DB
-- SQL is written with PostgreSQL syntax

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE organizations
(
    id          UUID PRIMARY KEY,
    name        TEXT UNIQUE NOT NULL,
    description TEXT,
    created     TIMESTAMP WITHOUT TIME ZONE NOT NULL
);

CREATE TABLE memberships
(
    "organization" UUID REFERENCES organizations(id),
    "user"         UUID NOT NULL,
    created        TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    renewal        TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY ("organization", "user")
);

CREATE TABLE roles
(
    id          UUID PRIMARY KEY,
    name        TEXT UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE permissions
(
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL
);

CREATE TABLE user_roles
(
    "user" UUID,
    "role" UUID REFERENCES roles(id),
    PRIMARY KEY ("user", "role")
);

CREATE TABLE role_permissions
(
    "role" UUID REFERENCES roles(id),
    "permission" TEXT REFERENCES permissions(id),
    PRIMARY KEY ("role", "permission")
);

CREATE TABLE settings
(
    created              TIMESTAMP WITHOUT TIME ZONE NOT NULL PRIMARY KEY,
    default_organization UUID REFERENCES organizations(id),
    version              INTEGER NOT NULL
);

-- Create an administrator role
INSERT INTO roles (id, name, description)
VALUES ('00000000-0000-0000-0000-000000000000', 'Admin', 'Default role for admins.');

INSERT INTO permissions (id, name)
VALUES ('communicate_email', 'Send out information through e-mail');

INSERT INTO permissions (id, name)
VALUES ('communicate_sms', 'Send out information through SMS');

INSERT INTO permissions (id, name)
VALUES ('communicate_newsfeed', 'Add or edit information displayed for user''s on their dashboard');

INSERT INTO permissions (id, name)
VALUES ('create_members', 'Add new members');

INSERT INTO permissions (id, name)
VALUES ('get_members', 'Get information about other members');

INSERT INTO permissions (id, name)
VALUES ('edit_members', 'Edit information about other members');

INSERT INTO permissions (id, name)
VALUES ('delete_members', 'Delete other members (only removes the membership, if the person has no memberships left then it will be deleted)');

INSERT INTO permissions (id, name)
VALUES ('create_organizations', 'Add new organizations');

INSERT INTO permissions (id, name)
VALUES ('edit_organizations', 'Edit information about the organizations');

INSERT INTO permissions (id, name)
VALUES ('delete_organizations', 'Delete organizations');

INSERT INTO permissions (id, name)
VALUES ('global', 'Don''t restrict this user''s permission to an organization or a geographic area');

INSERT INTO role_permissions ("role", "permission")
VALUES ('00000000-0000-0000-0000-000000000000', 'communicate_email');

INSERT INTO role_permissions ("role", "permission")
VALUES ('00000000-0000-0000-0000-000000000000', 'communicate_sms');

INSERT INTO role_permissions ("role", "permission")
VALUES ('00000000-0000-0000-0000-000000000000', 'communicate_newsfeed');

INSERT INTO role_permissions ("role", "permission")
VALUES ('00000000-0000-0000-0000-000000000000', 'create_members');

INSERT INTO role_permissions ("role", "permission")
VALUES ('00000000-0000-0000-0000-000000000000', 'get_members');

INSERT INTO role_permissions ("role", "permission")
VALUES ('00000000-0000-0000-0000-000000000000', 'edit_members');

INSERT INTO role_permissions ("role", "permission")
VALUES ('00000000-0000-0000-0000-000000000000', 'delete_members');

INSERT INTO role_permissions ("role", "permission")
VALUES ('00000000-0000-0000-0000-000000000000', 'create_organizations');

INSERT INTO role_permissions ("role", "permission")
VALUES ('00000000-0000-0000-0000-000000000000', 'edit_organizations');

INSERT INTO role_permissions ("role", "permission")
VALUES ('00000000-0000-0000-0000-000000000000', 'delete_organizations');

INSERT INTO role_permissions ("role", "permission")
VALUES ('00000000-0000-0000-0000-000000000000', 'global');

-- Create an organization
INSERT INTO organizations (id, name, description, created)
VALUES ('00000000-0000-0000-0000-000000000000', 'Ship#01', 'Default organization for Crew DB.', localtimestamp);

INSERT INTO settings (created, default_organization, version)
VALUES (localtimestamp, '00000000-0000-0000-0000-000000000000', 3);