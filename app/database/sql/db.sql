-- Database structure for Memberport
-- SQL is written with PostgreSQL syntax

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS ltree;

CREATE TABLE organizations
(
    id          UUID PRIMARY KEY,
    name        TEXT UNIQUE NOT NULL,
    description TEXT,
    active      BOOLEAN NOT NULL,
    created     TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    path        ltree
);

CREATE INDEX organization_path_idx ON organizations USING GIST (path);

CREATE TABLE users
(
    kratos_id     UUID PRIMARY KEY,
    member_number SERIAL UNIQUE NOT NULL,
    created       TIMESTAMP WITHOUT TIME ZONE NOT NULL
);

CREATE TABLE memberships
(
    id             UUID UNIQUE NOT NULL,
    "organization" UUID REFERENCES organizations(id),
    "user"         UUID REFERENCES users(kratos_id),
    created        TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    renewal        TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY ("organization", "user")
);

CREATE TABLE ended_memberships
(
    id             UUID PRIMARY KEY,
    "organization" UUID REFERENCES organizations(id),
    reason         TEXT NOT NULL,
    ended          TIMESTAMP WITHOUT TIME ZONE NOT NULL
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
    feed_url             TEXT NOT NULL,
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
    name      TEXT NOT NULL,
    created   TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    "country" UUID REFERENCES countries(id) NOT NULL,
    path      ltree
);

CREATE INDEX area_path_idx ON areas USING GIST (path);

CREATE TABLE municipalities
(
    id        UUID PRIMARY KEY,
    name      TEXT NOT NULL,
    created   TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    "country" UUID REFERENCES countries(id) NOT NULL,
    "area"    INTEGER REFERENCES areas(id)
);

CREATE TABLE organization_country
(
    "organization" UUID REFERENCES organizations(id),
    "country"      UUID REFERENCES countries(id),
    PRIMARY KEY ("organization", "country")
);

CREATE TABLE organization_area
(
    "organization" UUID REFERENCES organizations(id),
    "area"         INTEGER REFERENCES areas(id),
    PRIMARY KEY ("organization", "area")
);

CREATE TABLE organization_municipality
(
    "organization" UUID REFERENCES organizations(id),
    "municipality" UUID REFERENCES municipalities(id),
    PRIMARY KEY ("organization", "municipality")
);

CREATE TABLE posts
(
    id      UUID PRIMARY KEY,
    title   TEXT NOT NULL,
    content TEXT NOT NULL,
    author  UUID REFERENCES users(kratos_id) NOT NULL,
    created TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated TIMESTAMP WITHOUT TIME ZONE NOT NULL
);

CREATE TABLE post_organization
(
    "post"         UUID REFERENCES posts(id),
    "organization" UUID REFERENCES organizations(id),
    PRIMARY KEY ("post", "organization")
);

CREATE TABLE post_country
(
    "post"         UUID REFERENCES posts(id),
    "country" UUID REFERENCES countries(id),
    PRIMARY KEY ("post", "country")
);

CREATE TABLE post_area
(
    "post" UUID REFERENCES posts(id),
    "area" INTEGER REFERENCES areas(id),
    PRIMARY KEY ("post", "area")
);

CREATE TABLE post_municipality
(
    "post"         UUID REFERENCES posts(id),
    "municipality" UUID REFERENCES municipalities(id),
    PRIMARY KEY ("post", "municipality")
);

CREATE TABLE ics_links
(
    id          UUID PRIMARY KEY,
    description TEXT NOT NULL,
    ics_url     TEXT NOT NULL,
    created     TIMESTAMP WITHOUT TIME ZONE NOT NULL
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

INSERT INTO settings (initialized, created, default_organization, feed_url, version)
VALUES (FALSE, localtimestamp, NULL, '', 3);