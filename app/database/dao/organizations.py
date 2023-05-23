from app.logger import logger

from datetime import datetime
from typing import Union
from uuid import uuid4, UUID

from asyncpg import Connection
from asyncpg.exceptions import UniqueViolationError

from app.models import Organization
from app.database.dao.member_org import MemberOrgDao


class OrganizationsDao(MemberOrgDao):
    async def create_organization(
        self,
        name: str,
        description: str,
        active: bool,
        show_on_signup: bool,
        parent_id: Union[UUID, None],
        countries: Union[list, None] = None,
        areas: Union[list, None] = None,
        municipalities: Union[list, None] = None
    ) -> Union[Organization, None]:
        sql = """INSERT INTO mp_organizations (id, name, description, active, created, show_on_signup, path)
                 VALUES ($1, $2, $3, $4, $5, $6, $7);"""

        id = uuid4()
        created = datetime.utcnow()

        path = await self._get_path(parent_id, id)
        path_db = self._convert_to_db_path(path)

        try:
            async with self.pool.acquire() as con:
                await con.execute(sql, id, name, description, active, created, show_on_signup, path_db)
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
        organization.show_on_signup = show_on_signup
        organization.created = created
        organization.path = path

        return organization

    async def _get_path(self, parent_id: Union[UUID, None], org_id: UUID) -> str:
        if parent_id is None:
            return org_id.__str__()
        elif parent_id == org_id:
            return org_id.__str__()

        path = ""
        sql = 'SELECT path FROM mp_organizations WHERE id = $1;'

        try:
            async with self.pool.acquire() as con:
                path_db = await con.fetchval(sql, parent_id)
                path = self._convert_from_db_path(path_db)
        except Exception:
            logger.error("An error occured when trying to retrieve the path for new organization!", stack_info=True)
            return org_id.__str__()

        path += "." + org_id.__str__()
        logger.debug("Path for new organization: " + path)

        return path

    async def add_recruitment_areas(self, org_id: UUID, areas: Union[list, None]) -> None:
        try:
            await self._add_recruitment_areas(org_id, "area", areas, None)
        except Exception:
            logger.error("An error occured when trying to add recruitment areas to org: " + org_id.__str__(), stack_info=True)

    async def add_recruitment_countries(self, org_id: UUID, areas: Union[list, None]) -> None:
        try:
            await self._add_recruitment_areas(org_id, "country", areas, None)
        except Exception:
            logger.error("An error occured when trying to add recruitment countries to org: " + org_id.__str__(), stack_info=True)

    async def add_recruitment_municipalities(self, org_id: UUID, areas: Union[list, None]) -> None:
        try:
            await self._add_recruitment_areas(org_id, "municipality", areas, None)
        except Exception:
            logger.error("An error occured when trying to add recruitment municipalities to org: " + org_id.__str__(), stack_info=True)

    async def _add_recruitment_areas(self, org_id: UUID, area_type: str, areas: Union[list, None], con: Union[Connection, None]) -> None:
        if areas is None or (area_type != "country" and area_type != "area" and area_type != "municipality"):
            return

        if con is None:
            con = await self.pool.acquire()

        sql = 'INSERT INTO mp_organization_country ("organization", "country") VALUES ($1, $2);'
        sql = sql.replace("country", area_type)

        for area in areas:
            try:
                await con.execute(sql, org_id, area)
            except UniqueViolationError as exc:
                logger.debug(exc.__str__())
                logger.warning("Tried to insert recruitment area: " + str(area) + " but the relation already existed")

    async def get_recruitment_countries(self, org_id: UUID) -> list:
        sql = 'SELECT "country" FROM mp_organization_country WHERE "organization" = $1;'
        country_ids = list()

        try:
            async with self.pool.acquire() as con:
                rows = await con.fetch(sql, org_id)
        except Exception as exc:
            logger.debug(exc.__str__())
            logger.error("An error occured when trying to retrieve recruitment country", stack_info=True)

        for row in rows:
            country_ids.append(row["country"])

        return country_ids

    async def get_recruitment_areas(self, org_id: UUID) -> list:
        sql = 'SELECT "area" FROM mp_organization_area WHERE "organization" = $1;'
        area_ids = list()

        try:
            async with self.pool.acquire() as con:
                rows = await con.fetch(sql, org_id)
        except Exception as exc:
            logger.debug(exc.__str__())
            logger.error("An error occured when trying to retrieve recruitment area", stack_info=True)

        for row in rows:
            area_ids.append(row["area"])

        return area_ids

    async def get_recruitment_municipalities(self, org_id: UUID) -> list:
        sql = 'SELECT "municipality" FROM mp_organization_municipality WHERE "organization" = $1;'
        municipality_ids = list()

        try:
            async with self.pool.acquire() as con:
                rows = await con.fetch(sql, org_id)
        except Exception as exc:
            logger.debug(exc.__str__())
            logger.error("An error occured when trying to retrieve recruitment municipality", stack_info=True)

        for row in rows:
            municipality_ids.append(row["municipality"])

        return municipality_ids

    async def set_recruitment_areas(self, org_id: UUID, countries: list, areas: list, municipalities: list) -> bool:
        async with self.pool.acquire() as con:
            try:
                async with con.transaction():
                    await self._remove_all_recruitment(org_id, con)
                    await self._add_recruitment_areas(org_id, "country", countries, con)
                    await self._add_recruitment_areas(org_id, "area", areas, con)
                    await self._add_recruitment_areas(org_id, "municipality", municipalities, con)
            except Exception:
                logger.error("An error occured when trying to set recruitment areas!", stack_info=True)
                return False

        return True

    async def _remove_all_recruitment(self, org_id: UUID, con: Connection) -> bool:
        sql_country = 'DELETE FROM mp_organization_country WHERE "organization" = $1;'
        sql_area = 'DELETE FROM mp_organization_area WHERE "organization" = $1;'
        sql_municipality = 'DELETE FROM mp_organization_municipality WHERE "organization" = $1;'

        await con.execute(sql_country, org_id)
        await con.execute(sql_area, org_id)
        await con.execute(sql_municipality, org_id)

    async def get_default_organization(self) -> Union[Organization, None]:
        sql = "SELECT default_organization FROM mp_settings;"

        try:
            async with self.pool.acquire() as con:
                row = await con.fetchrow(sql)
        except Exception:
            logger.error("An error occured when trying to retrieve the default organization!", stack_info=True)
            return None

        if row["default_organization"] is None:
            logger.debug("No default organization found...")
            return None

        return await self.get_organization_by_id(row["default_organization"])

    async def get_organization_by_name(self, name: str) -> Union[Organization, None]:
        sql = "SELECT id, description, active, created, show_on_signup, path FROM mp_organizations WHERE name = $1"

        try:
            async with self.pool.acquire() as con:
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
        organization.description = row["description"]
        organization.active = row["active"]
        organization.created = row["created"]
        organization.show_on_signup = row["show_on_signup"]
        organization.path = self._convert_from_db_path(row["path"])

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
            sql = """ SELECT o.id, o.name, o.description, o.created, o.active, o.show_on_signup, o.path
                      FROM mp_organizations o
                      ORDER BY """
            sql = sql + order_column + " " + order_dir + ";"  # order_column and order_dir have fixed values so no SQL injection is possible

            async with self.pool.acquire() as con:
                rows = await con.fetch(sql)
        else:
            search = "%"+search+"%"
            sql = """ SELECT o.id, o.name, o.description, o.created, o.active, o.show_on_signup, o.path
                      FROM mp_organizations o
                      WHERE o.name LIKE $1
                      OR o.description LIKE $1
                      OR to_char(o.created, 'YYYY-MM-DD HH24:MI:SS.US') LIKE $1
                      ORDER BY """
            sql = sql + order_column + " " + order_dir + ";"  # order_column and order_dir have fixed values so no SQL injection is possible

            async with self.pool.acquire() as con:
                rows = await con.fetch(sql, search)

        organizations = list()
        self.convert_rows_to_organizations(organizations, rows)

        return organizations

    async def get_organizations_in_area(self, country_id: UUID, areas: list, municipality_id: UUID,
                                        filter: Union[list, None] = None) -> list:
        sql = """SELECT o.id, o.name, o.description, o.active, o.created, o.show_on_signup, o.path FROM mp_organization_country
                 INNER JOIN mp_organizations AS o ON mp_organization_country.organization = o.id WHERE country = $1;"""
        try:
            async with self.pool.acquire() as con:
                rows = await con.fetch(sql, country_id)
        except Exception as exc:
            logger.debug(exc.__str__())

        organizations = list()

        self.convert_rows_to_organizations(organizations, rows)

        sql = """SELECT o.id, o.name, o.description, o.active, o.created, o.show_on_signup, o.path FROM mp_organization_area
               INNER JOIN mp_organizations AS o ON mp_organization_area.organization = o.id WHERE area = $1;"""

        for area_id in areas:
            try:
                async with self.pool.acquire() as con:
                    rows = await con.fetch(sql, area_id)
            except Exception as exc:
                logger.debug(exc.__str__())
            self.convert_rows_to_organizations(organizations, rows)

        sql = """SELECT o.id, o.name, o.description, o.active, o.created, o.show_on_signup, o.path FROM mp_organization_municipality
               INNER JOIN mp_organizations AS o ON mp_organization_municipality.organization = o.id WHERE municipality = $1;"""
        try:
            async with self.pool.acquire() as con:
                rows = await con.fetch(sql, municipality_id)
        except Exception as exc:
            logger.debug(exc.__str__())

        self.convert_rows_to_organizations(organizations, rows)

        if filter is not None:
            organizations = list(set(organizations) - set(filter))

        return organizations

    async def update_organization(
        self,
        id:
        UUID,
        name:
        str, description: str,
        active: bool,
        show_on_signup: bool,
        update_parent: bool,
        parent_id: Union[UUID, None]
    ) -> Union[Organization, None]:
        sql = "UPDATE mp_organizations SET name = $1, description = $2, active = $3, show_on_signup = $4 WHERE id = $5"

        try:
            async with self.pool.acquire() as con:
                async with con.transaction():
                    await con.execute(sql, name, description, active, show_on_signup, id)

                    if update_parent is True:
                        path = (await self._get_path(parent_id, id)).removesuffix('.' + id.__str__())
                        if path == id.__str__():
                            path = ""

                        if path.find(id.__str__()) != -1:
                            raise ValueError("Organization can't be a child to itself: " + path)

                        if path == "" and parent_id is not None and parent_id != id:
                            raise ValueError("Organization with ID: " + parent_id.__str__() + " was not found")

                        path_db = self._convert_to_db_path(path)
                        source_path = await con.fetchval('SELECT path FROM mp_organizations WHERE id = $1;', id)
                        sql = 'UPDATE mp_organizations SET path = $1 || SUBPATH(path, nlevel($2)-1) WHERE path <@ $2;'
                        await con.execute(sql, path_db, source_path)
        except UniqueViolationError as exc:
            logger.debug(exc.__str__())
            logger.warning("Tried to update organization: " + str(id))
            return None
        except Exception as exc:
            logger.debug(exc.__str__())
            logger.warning("Something went wrong when trying to update organization: " + str(id))
            return None

        return await self.get_organization_by_id(id)

    async def delete_organization(self, id: UUID) -> bool:
        success = await self.remove_memberships_from_org(id)
        if not success:
            return False

        async with self.pool.acquire() as con:
            try:
                async with con.transaction():
                    # NULL default_organization if were removing default
                    await con.execute("UPDATE settings SET default_organization = NULL WHERE default_organization = $1;", id)
                    rows = await con.fetch(
                        "SELECT id FROM mp_organizations WHERE path <@ (SELECT path FROM mp_organizations WHERE id = $1);",
                        id
                    )
                    for row in rows:
                        await self._remove_all_recruitment(row["id"], con)

                    await con.execute("DELETE FROM mp_organizations WHERE path <@ (SELECT path FROM mp_organizations WHERE id = $1);", id)
            except Exception as exc:
                logger.debug(exc.__str__())
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
            organization.show_on_signup = row["show_on_signup"]
            organization.path = self._convert_from_db_path(row["path"])
            organizations.append(organization)

        return organizations

    async def get_organizations_for_signup(self):
        sql = """SELECT o.id, o.name, o.description, o.created, o.active, o.show_on_signup, o.path
                 FROM mp_organizations o
                 WHERE o.show_on_signup is TRUE
                 ORDER BY name ASC;"""

        async with self.pool.acquire() as con:
            rows = await con.fetch(sql)

        organizations = list()
        self.convert_rows_to_organizations(organizations, rows)

        return organizations
