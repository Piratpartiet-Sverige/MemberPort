-- Database structure for Crew DB
-- SQL is written with PostgreSQL syntax

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE organizations
(
    id          UUID PRIMARY KEY,
    name        TEXT UNIQUE NOT NULL,
    description TEXT,
    active      BOOLEAN NOT NULL,
    created     TIMESTAMP WITHOUT TIME ZONE NOT NULL
);

CREATE TABLE users
(
    kratos_id     UUID PRIMARY KEY,
    member_number SERIAL UNIQUE NOT NULL,
    created       TIMESTAMP WITHOUT TIME ZONE NOT NULL
);

CREATE TABLE memberships
(
    "organization" UUID REFERENCES organizations(id),
    "user"         UUID REFERENCES users(kratos_id),
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
    "user" UUID REFERENCES users(kratos_id),
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
    initialized          BOOLEAN NOT NULL,
    created              TIMESTAMP WITHOUT TIME ZONE NOT NULL PRIMARY KEY,
    default_organization UUID REFERENCES organizations(id),
    version              INTEGER NOT NULL
);

CREATE TABLE countries
(
    id      UUID PRIMARY KEY,
    name    TEXT NOT NULL,
    created TIMESTAMP WITHOUT TIME ZONE NOT NULL
);

CREATE TABLE areas
(
    id        SERIAL PRIMARY KEY,
    created   TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    "country" UUID REFERENCES countries(id)
);

CREATE TABLE municipalities
(
    id        UUID PRIMARY KEY,
    name      TEXT NOT NULL,
    created   TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    "country" UUID REFERENCES countries(id),
    "area"    INTEGER REFERENCES areas(id)
);

CREATE TABLE area_paths
(
    "ancestor"   INTEGER REFERENCES areas(id) NOT NULL,
    "descendent" INTEGER REFERENCES areas(id) NOT NULL,
    depth        INTEGER NOT NULL,
    PRIMARY KEY  ("ancestor", "descendent")
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

INSERT INTO countries (id, name, created)
VALUES ('00000000-0000-0000-0000-000000000000', 'Sverige', localtimestamp);

INSERT INTO municipalities (id, name, created, "country", "area")
VALUES (uuid_generate_v4(), 'Ale kommun', localtimestamp, '00000000-0000-0000-0000-000000000000', NULL);

INSERT INTO municipalities (id, name, created, "country", "area")
VALUES (uuid_generate_v4(), 'Alingsås kommun', localtimestamp, '00000000-0000-0000-0000-000000000000', NULL);

INSERT INTO municipalities (id, name, created, "country", "area")
VALUES (uuid_generate_v4(), 'Alvesta kommun', localtimestamp, '00000000-0000-0000-0000-000000000000', NULL);

INSERT INTO municipalities (id, name, created, "country", "area")
VALUES (uuid_generate_v4(), 'Aneby kommun', localtimestamp, '00000000-0000-0000-0000-000000000000', NULL);

INSERT INTO municipalities (id, name, created, "country", "area")
VALUES (uuid_generate_v4(), 'Arboga kommun', localtimestamp, '00000000-0000-0000-0000-000000000000', NULL);

INSERT INTO municipalities (id, name, created, "country", "area")
VALUES (uuid_generate_v4(), 'Arjeplogs kommun', localtimestamp, '00000000-0000-0000-0000-000000000000', NULL);

INSERT INTO municipalities (id, name, created, "country", "area")
VALUES (uuid_generate_v4(), 'Arvidsjaurs kommun', localtimestamp, '00000000-0000-0000-0000-000000000000', NULL);

INSERT INTO municipalities (id, name, created, "country", "area")
VALUES (uuid_generate_v4(), 'Arvika kommun', localtimestamp, '00000000-0000-0000-0000-000000000000', NULL);

INSERT INTO municipalities (id, name, created, "country", "area")
VALUES (uuid_generate_v4(), 'Askersunds kommun', localtimestamp, '00000000-0000-0000-0000-000000000000', NULL);

INSERT INTO municipalities (id, name, created, "country", "area")
VALUES (uuid_generate_v4(), 'Avesta kommun', localtimestamp, '00000000-0000-0000-0000-000000000000', NULL);

INSERT INTO municipalities (id, name, created, "country", "area")
VALUES (uuid_generate_v4(), 'Bengtsfors kommun', localtimestamp, '00000000-0000-0000-0000-000000000000', NULL);

INSERT INTO municipalities (id, name, created, "country", "area")
VALUES (uuid_generate_v4(), 'Bergs kommun', localtimestamp, '00000000-0000-0000-0000-000000000000', NULL);

INSERT INTO municipalities (id, name, created, "country", "area")
VALUES (uuid_generate_v4(), 'Bjurholms kommun', localtimestamp, '00000000-0000-0000-0000-000000000000', NULL);

INSERT INTO municipalities (id, name, created, "country", "area")
VALUES (uuid_generate_v4(), 'Bjuvs kommun', localtimestamp, '00000000-0000-0000-0000-000000000000', NULL);

INSERT INTO municipalities (id, name, created, "country", "area")
VALUES (uuid_generate_v4(), 'Bodens kommun', localtimestamp, '00000000-0000-0000-0000-000000000000', NULL);

INSERT INTO municipalities (id, name, created, "country", "area")
VALUES (uuid_generate_v4(), 'Bollebygds kommun', localtimestamp, '00000000-0000-0000-0000-000000000000', NULL);

INSERT INTO settings (initialized, created, default_organization, version)
VALUES (FALSE, localtimestamp, NULL, 3);