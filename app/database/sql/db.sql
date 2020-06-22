-- Database structure for Crew DB
-- SQL is written with PostgreSQL syntax

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE settings
(
    created TIMESTAMP WITHOUT TIME ZONE NOT NULL PRIMARY KEY,
    version INTEGER NOT NULL
);

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
    id          UUID PRIMARY KEY,
    name        TEXT UNIQUE NOT NULL,
    description TEXT
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
    "permission" UUID REFERENCES permissions(id),
    PRIMARY KEY ("role", "permission")
);

-- Create an administrator role
INSERT INTO roles (id, name, description)
VALUES ('00000000-0000-0000-0000-000000000000', 'Admin', 'Default role for admins.');

-- Create an organization
INSERT INTO organizations (id, name, description, created)
VALUES ('00000000-0000-0000-0000-000000000000', 'Ship#01', 'Default organization for Crew DB.', localtimestamp);

INSERT INTO settings (created, version)
VALUES (localtimestamp, 2);