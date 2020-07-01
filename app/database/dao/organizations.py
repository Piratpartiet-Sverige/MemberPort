from app.logger import logger

from datetime import datetime
from hashlib import sha256
from typing import Union
from uuid import uuid4, UUID

from asyncpg import Connection
from asyncpg.pool import Pool
from asyncpg.exceptions import UniqueViolationError
from bcrypt import checkpw, hashpw, gensalt

from app.database.dao.emails import EmailDao
from app.models import Organization
from app.email import send_email


class OrganizationsDao:
    def __init__(self, pool: Pool):
        self.pool = pool

    async def get_default_organization() -> Union[Organization, None]:
        sql = "SELECT default_organization FROM settings"

        try:
            async with self.pool.acquire() as con:  # type: Connection
                row = await con.fetchrow(sql)
        except Exception:
            logger.error("An error occured when trying to retrieve the default organization!", stack_info=True)
            return None
        
        if row["default_organization"] is None:
            logger.debug("No default organization found...")
            return None

        return await self.get_organization_by_id(row["default_organization"])

    async def get_organization_by_id(id: UUID) -> Union[Organization, None]:
        sql = "SELECT name, description, created FROM organizations WHERE id = $1"

        try:
            async with self.pool.acquire() as con:  # type: Connection
                row = await con.fetchrow(sql, id)
        except Exception:
            logger.error("An error occured when trying to retrieve an organization!", stack_info=True)
            return None

        if row is None:
            logger.debug("No  organization found with ID: " + str(id))
            return None

        organization = Organization()
        organization.id = id
        organization.name = row["name"]
        organization.name = row["description"]
        organization.name = row["created"]

        return organization

    async def get_organization_by_name(name: str) -> Union[Organization, None]:
        sql = "SELECT id, description, created FROM organizations WHERE name = $1"

        try:
            async with self.pool.acquire() as con:  # type: Connection
                row = await con.fetchrow(sql, name)
        except Exception:
            logger.error("An error occured when trying to retrieve an organization!", stack_info=True)
            return None

        if row is None:
            logger.debug("No  organization found with name: " + name)
            return None

        organization = Organization()
        organization.id = row["id"]
        organization.name = name
        organization.name = row["description"]
        organization.name = row["created"]

        return organization

    async def get_organizations(self, search: str, order_column: str, order_dir_asc: bool) -> list:
        """
        Get a list of all organizations
        :return: A list filled dicts
        """
        order_dir = "DESC"

        if order_dir_asc is True:
            order_dir = "ASC"

        if order_column != "name" and order_column != "email" and order_column != "created":
            order_column = "name"

        if search == "":
            sql = """ SELECT o.id, o.name, o.description, o.created
                      FROM organizations o
                      ORDER BY """ + order_column + " " + order_dir + ";"

            async with self.pool.acquire() as con:  # type: Connection
                rows = await con.fetch(sql)
        else:
            search = "%"+search+"%"
            sql = """ SELECT o.id, o.name, o.description, o.created
                      FROM organizations o
                      WHERE o.name LIKE $1
                      OR o.description LIKE $1
                      OR to_char(o.created, 'YYYY-MM-DD HH24:MI:SS.US') LIKE $1
                      ORDER BY """ + order_column + " " + order_dir + ";"

            async with self.pool.acquire() as con:  # type: Connection
                rows = await con.fetch(sql, search)

        organizations = []
        for row in rows:
            organization = Organization()
            organization.id = row["id"]
            organization.name = row["name"]
            organization.description = row["description"]
            organization.created = row["created"]

            organizations.append(organization)

        return organizations
