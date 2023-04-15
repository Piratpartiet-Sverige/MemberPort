-- Database structure for Memberport
-- SQL is written with PostgreSQL syntax

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS ltree;

CREATE TABLE mp_organizations
(
    id             UUID PRIMARY KEY,
    name           TEXT UNIQUE NOT NULL,
    description    TEXT,
    active         BOOLEAN NOT NULL,
    created        TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    show_on_signup BOOLEAN NOT NULL,
    path           ltree
);

CREATE INDEX mp_organization_path_idx ON mp_organizations USING GIST (path);

CREATE SEQUENCE mp_membernumber MINVALUE 1;

CREATE TABLE mp_memberships
(
    id             UUID UNIQUE NOT NULL,
    "organization" UUID REFERENCES mp_organizations(id),
    "user"         UUID REFERENCES identities(id),
    created        TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    renewal        TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY ("organization", "user")
);

CREATE TABLE mp_ended_memberships
(
    id             UUID PRIMARY KEY,
    "organization" UUID REFERENCES mp_organizations(id),
    reason         TEXT NOT NULL,
    ended          TIMESTAMP WITHOUT TIME ZONE NOT NULL
);

CREATE TABLE mp_roles
(
    id          UUID PRIMARY KEY,
    name        TEXT UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE mp_permissions
(
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL
);

CREATE TABLE mp_user_roles
(
    "user" UUID REFERENCES identities(id),
    "role" UUID REFERENCES mp_roles(id),
    PRIMARY KEY ("user", "role")
);

CREATE TABLE mp_role_permissions
(
    "role" UUID REFERENCES mp_roles(id),
    "permission" TEXT REFERENCES mp_permissions(id),
    PRIMARY KEY ("role", "permission")
);

CREATE TABLE mp_settings
(
    initialized          BOOLEAN NOT NULL,
    created              TIMESTAMP WITHOUT TIME ZONE NOT NULL PRIMARY KEY,
    default_organization UUID REFERENCES mp_organizations(id),
    feed_url             TEXT NOT NULL,
    version              INTEGER NOT NULL
);

CREATE TABLE mp_countries
(
    id      UUID PRIMARY KEY,
    name    TEXT NOT NULL,
    created TIMESTAMP WITHOUT TIME ZONE NOT NULL
);

CREATE TABLE mp_areas
(
    id        SERIAL PRIMARY KEY,
    name      TEXT NOT NULL,
    created   TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    "country" UUID REFERENCES mp_countries(id) NOT NULL,
    path      ltree
);

CREATE INDEX mp_area_path_idx ON mp_areas USING GIST (path);

CREATE TABLE mp_municipalities
(
    id        UUID PRIMARY KEY,
    name      TEXT NOT NULL,
    created   TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    "country" UUID REFERENCES mp_countries(id) NOT NULL,
    "area"    INTEGER REFERENCES mp_areas(id)
);

CREATE TABLE mp_organization_country
(
    "organization" UUID REFERENCES mp_organizations(id),
    "country"      UUID REFERENCES mp_countries(id),
    PRIMARY KEY ("organization", "country")
);

CREATE TABLE mp_organization_area
(
    "organization" UUID REFERENCES mp_organizations(id),
    "area"         INTEGER REFERENCES mp_areas(id),
    PRIMARY KEY ("organization", "area")
);

CREATE TABLE mp_organization_municipality
(
    "organization" UUID REFERENCES mp_organizations(id),
    "municipality" UUID REFERENCES mp_municipalities(id),
    PRIMARY KEY ("organization", "municipality")
);

CREATE TABLE mp_posts
(
    id      UUID PRIMARY KEY,
    title   TEXT NOT NULL,
    content TEXT NOT NULL,
    author  UUID REFERENCES identities(id) NOT NULL,
    created TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated TIMESTAMP WITHOUT TIME ZONE NOT NULL
);

CREATE TABLE mp_post_organization
(
    "post"         UUID REFERENCES mp_posts(id),
    "organization" UUID REFERENCES mp_organizations(id),
    PRIMARY KEY ("post", "organization")
);

CREATE TABLE mp_post_country
(
    "post"         UUID REFERENCES mp_posts(id),
    "country" UUID REFERENCES mp_countries(id),
    PRIMARY KEY ("post", "country")
);

CREATE TABLE mp_post_area
(
    "post" UUID REFERENCES mp_posts(id),
    "area" INTEGER REFERENCES mp_areas(id),
    PRIMARY KEY ("post", "area")
);

CREATE TABLE mp_post_municipality
(
    "post"         UUID REFERENCES mp_posts(id),
    "municipality" UUID REFERENCES mp_municipalities(id),
    PRIMARY KEY ("post", "municipality")
);

CREATE TABLE mp_ics_links
(
    id          UUID PRIMARY KEY,
    description TEXT NOT NULL,
    ics_url     TEXT NOT NULL,
    created     TIMESTAMP WITHOUT TIME ZONE NOT NULL
);

-- Create an administrator role
INSERT INTO mp_roles (id, name, description)
VALUES ('00000000-0000-0000-0000-000000000000', 'Admin', 'Default role for admins.');

INSERT INTO mp_permissions (id, name)
VALUES ('communicate_email', 'Send out information through e-mail');

INSERT INTO mp_permissions (id, name)
VALUES ('communicate_sms', 'Send out information through SMS');

INSERT INTO mp_permissions (id, name)
VALUES ('communicate_newsfeed', 'Add or edit information displayed for user''s on their dashboard');

INSERT INTO mp_permissions (id, name)
VALUES ('create_members', 'Add new members');

INSERT INTO mp_permissions (id, name)
VALUES ('get_members', 'Get information about other members');

INSERT INTO mp_permissions (id, name)
VALUES ('edit_members', 'Edit information about other members');

INSERT INTO mp_permissions (id, name)
VALUES ('delete_members', 'Delete other members (only removes the membership, if the person has no memberships left then it will be deleted)');

INSERT INTO mp_permissions (id, name)
VALUES ('create_organizations', 'Add new organizations');

INSERT INTO mp_permissions (id, name)
VALUES ('edit_organizations', 'Edit information about the organizations');

INSERT INTO mp_permissions (id, name)
VALUES ('delete_organizations', 'Delete organizations');

INSERT INTO mp_permissions (id, name)
VALUES ('edit_geography', 'Edit geography tree');

INSERT INTO mp_permissions (id, name)
VALUES ('edit_calendar', 'Edit calendars');

INSERT INTO mp_permissions (id, name)
VALUES ('global', 'Don''t restrict this user''s permission to an organization or a geographic area');

INSERT INTO mp_role_permissions ("role", "permission")
VALUES ('00000000-0000-0000-0000-000000000000', 'communicate_email');

INSERT INTO mp_role_permissions ("role", "permission")
VALUES ('00000000-0000-0000-0000-000000000000', 'communicate_sms');

INSERT INTO mp_role_permissions ("role", "permission")
VALUES ('00000000-0000-0000-0000-000000000000', 'communicate_newsfeed');

INSERT INTO mp_role_permissions ("role", "permission")
VALUES ('00000000-0000-0000-0000-000000000000', 'create_members');

INSERT INTO mp_role_permissions ("role", "permission")
VALUES ('00000000-0000-0000-0000-000000000000', 'get_members');

INSERT INTO mp_role_permissions ("role", "permission")
VALUES ('00000000-0000-0000-0000-000000000000', 'edit_members');

INSERT INTO mp_role_permissions ("role", "permission")
VALUES ('00000000-0000-0000-0000-000000000000', 'delete_members');

INSERT INTO mp_role_permissions ("role", "permission")
VALUES ('00000000-0000-0000-0000-000000000000', 'create_organizations');

INSERT INTO mp_role_permissions ("role", "permission")
VALUES ('00000000-0000-0000-0000-000000000000', 'edit_organizations');

INSERT INTO mp_role_permissions ("role", "permission")
VALUES ('00000000-0000-0000-0000-000000000000', 'delete_organizations');

INSERT INTO mp_role_permissions ("role", "permission")
VALUES ('00000000-0000-0000-0000-000000000000', 'edit_geography');

INSERT INTO mp_role_permissions ("role", "permission")
VALUES ('00000000-0000-0000-0000-000000000000', 'edit_calendar');

INSERT INTO mp_role_permissions ("role", "permission")
VALUES ('00000000-0000-0000-0000-000000000000', 'global');

INSERT INTO mp_settings (initialized, created, default_organization, feed_url, version)
VALUES (FALSE, localtimestamp, NULL, '', 3);