from app.logger import logger

from datetime import datetime
from typing import Union
from uuid import uuid4, UUID

from asyncpg import Connection
from asyncpg.exceptions import UniqueViolationError

from app.models import Organization
from app.database.dao.member_org import MemberOrgDao


class OrganizationsDao(MemberOrgDao):
    async def create_organization(self, name: str, description: str, active: bool, countries: Union[list, None] = None,
                                  areas: Union[list, None] = None, municipalities: Union[list, None] = None) -> Union[Organization, None]:
        sql = "INSERT INTO organizations (id, name, description, active, created) VALUES ($1, $2, $3, $4, $5);"

        id = uuid4()
        created = datetime.utcnow()

        try:
            async with self.pool.acquire() as con:  # type: Connection
                await con.execute(sql, id, name, description, active, created)
        except UniqueViolationError as exc:
            logger.debug(exc.__str__())
            logger.warning("Tried to create organization: " + str(id) + " but organization already existed")
            return None

        await self.add_recruitment_countries(id, countries)
        await self.add_recruitment_areas(id, areas)
        await self.add_recruitment_municipalities(id, municipalities)

        organization = Organization()
        organization.id = id
        organization.name = name
        organization.description = description
        organization.active = active
        organization.created = created

        return organization

    async def add_recruitment_areas(self, org_id: UUID, areas: Union[list, None]) -> None:
        await self._add_recruitment_areas(org_id, "area", areas)

    async def add_recruitment_countries(self, org_id: UUID, areas: Union[list, None]) -> None:
        await self._add_recruitment_areas(org_id, "country", areas)

    async def add_recruitment_municipalities(self, org_id: UUID, areas: Union[list, None]) -> None:
        await self._add_recruitment_areas(org_id, "municipality", areas)

    async def _add_recruitment_areas(self, org_id: UUID, area_type: str, areas: Union[list, None]) -> None:
        if areas is None or (area_type != "country" and area_type != "area" and area_type != "municipality"):
            return

        sql = 'INSERT INTO organization_country ("organization", "country") VALUES ($1, $2);'
        sql = sql.replace("country", area_type)

        for area in areas:
            try:
                async with self.pool.acquire() as con:  # type: Connection
                    await con.execute(sql, org_id, area)
            except UniqueViolationError as exc:
                logger.debug(exc.__str__())
                logger.warning("Tried to insert recruitment area: " + str(area) + " but the relation already existed")

    async def get_default_organization(self) -> Union[Organization, None]:
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

    async def get_organization_by_name(self, name: str) -> Union[Organization, None]:
        sql = "SELECT id, description, created FROM organizations WHERE name = $1"

        try:
            async with self.pool.acquire() as con:  # type: Connection
                row = await con.fetchrow(sql, name)
        except Exception:
            logger.error("An error occured when trying to retrieve an organization by name!", stack_info=True)
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

        if order_column != "name" or order_column != "created":
            order_column = "name"

        if search == "":
            sql = """ SELECT o.id, o.name, o.description, o.created, o.active
                      FROM organizations o
                      ORDER BY """ + order_column + " " + order_dir + ";"  # noqa: S608 # nosec

            async with self.pool.acquire() as con:  # type: Connection
                rows = await con.fetch(sql)
        else:
            search = "%"+search+"%"
            sql = """ SELECT o.id, o.name, o.description, o.created, o.active
                      FROM organizations o
                      WHERE o.name LIKE $1
                      OR o.description LIKE $1
                      OR to_char(o.created, 'YYYY-MM-DD HH24:MI:SS.US') LIKE $1
                      ORDER BY """ + order_column + " " + order_dir + ";"  # noqa: S608 # nosec

            async with self.pool.acquire() as con:  # type: Connection
                rows = await con.fetch(sql, search)

        organizations = list()
        self.convert_rows_to_organizations(organizations, rows)

        return organizations

    async def get_organizations_in_area(self, country_id: UUID, areas: list, municipality_id: UUID) -> list:
        sql = """SELECT o.id, o.name, o.description, o.active, o.created FROM organization_country
                 INNER JOIN organizations AS o ON organization_country.organization = o.id WHERE country = $1;"""
        try:
            async with self.pool.acquire() as con:  # type: Connection
                rows = await con.fetch(sql, country_id)
        except Exception as exc:
            logger.debug(exc.__str__())

        organizations = list()

        self.convert_rows_to_organizations(organizations, rows)

        sql = """SELECT o.id, o.name, o.description, o.active, o.created FROM organization_area
               INNER JOIN organizations AS o ON organization_area.organization = o.id WHERE area = $1;"""

        for area_id in areas:
            try:
                async with self.pool.acquire() as con:  # type: Connection
                    rows = await con.fetch(sql, area_id)
            except Exception as exc:
                logger.debug(exc.__str__())
            self.convert_rows_to_organizations(organizations, rows)

        sql = """SELECT o.id, o.name, o.description, o.active, o.created FROM organization_municipality
               INNER JOIN organizations AS o ON organization_municipality.organization = o.id WHERE municipality = $1;"""
        try:
            async with self.pool.acquire() as con:  # type: Connection
                rows = await con.fetch(sql, municipality_id)
        except Exception as exc:
            logger.debug(exc.__str__())

        self.convert_rows_to_organizations(organizations, rows)

        return organizations

    async def update_organization(self, id: UUID, name: str, description: str, active: bool) -> Union[Organization, None]:
        sql = "UPDATE organizations SET name = $1, description = $2, active = $3 WHERE id = $4"

        try:
            async with self.pool.acquire() as con:  # type: Connection
                await con.execute(sql, name, description, active, id)
        except UniqueViolationError as exc:
            logger.debug(exc.__str__())
            logger.warning("Tried to update organization: " + str(id))
            return None

        return await self.get_organization_by_id(id)

    async def delete_organization(self, id: UUID) -> bool:
        success = await self.remove_memberships_from_org(id)
        if not success:
            return False

        # NULL default_organization if were removing default
        try:
            async with self.pool.acquire() as con:
                await con.execute("UPDATE settings SET default_organization = NULL WHERE default_organization = $1", id)
        except Exception:
            return False

        try:
            async with self.pool.acquire() as con:
                await con.execute("DELETE FROM organizations WHERE id = $1", id)
        except Exception:
            return False
        return True

    def convert_rows_to_organizations(self, organizations: list, rows: list) -> list:
        for row in rows:
            organization = Organization()
            organization.id = row["id"]
            organization.name = row["name"]
            organization.description = row["description"]
            organization.active = row["active"]
            organization.created = row["created"]
            organizations.append(organization)

        return organizations
