-- Database structure for Tornado Shelter
-- SQL is written with PostgreSQL syntax

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE users
(
    id                    UUID PRIMARY KEY,
    name                  TEXT NOT NULL,
    email                 TEXT UNIQUE NOT NULL,
    password              TEXT NOT NULL,
    password_force_change BOOLEAN NOT NULL DEFAULT FALSE,
    created               TIMESTAMP WITHOUT TIME ZONE NOT NULL
);

CREATE TABLE members
(
    "user"      UUID REFERENCES users(id),
    given_name  TEXT NOT NULL,
    last_name   TEXT NOT NULL,
    birth       DATE NOT NULL,
    postal_code TEXT NOT NULL,
    city        TEXT NOT NULL,
    address     TEXT NOT NULL,
    country     TEXT NOT NULL,
    PRIMARY KEY ("user")
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
    "user"         UUID REFERENCES users(id),
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
    "user" UUID REFERENCES users(id),
    "role" UUID REFERENCES roles(id),
    PRIMARY KEY ("user", "role")
);

CREATE TABLE role_permissions
(
    "role" UUID REFERENCES roles(id),
    "permission" UUID REFERENCES permissions(id),
    PRIMARY KEY ("role", "permission")
);

CREATE TABLE sessions
(
    id        UUID PRIMARY KEY,
    "user"    UUID REFERENCES users(id),
    hash      TEXT NOT NULL,
    created   TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    last_used TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    last_ip   TEXT NOT NULL
);

-- Create an administrator role
INSERT INTO roles (id, name, description)
VALUES ('00000000-0000-0000-0000-000000000000', 'Admin', 'Default role for admins.');

-- Create an administrator account with password "Admin1!" and then force a change upon first login
INSERT INTO users (id, name, email, password, password_force_change, created)
VALUES ('00000000-0000-0000-0000-000000000000', 'Admin', 'admin@localhost.org', '$2b$12$M8ttq7/ftdJHjiD69IBCQeFgUQqhUPben/txmJu9up02J7WXtitmq', true, localtimestamp);

-- Assign Admin role to the Admin user
INSERT INTO user_roles ("user", "role")
VALUES ('00000000-0000-0000-0000-000000000000', '00000000-0000-0000-0000-000000000000');

-- Create an organization
INSERT INTO organizations (id, name, description, created)
VALUES ('00000000-0000-0000-0000-000000000000', 'Ship#01', 'Default organization for Crew DB.', localtimestamp);
