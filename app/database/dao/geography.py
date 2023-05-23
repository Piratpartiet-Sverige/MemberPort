from datetime import datetime
from typing import Union
from uuid import uuid4, UUID

from asyncpg.exceptions import DataError, UniqueViolationError

from app.logger import logger
from app.models import Country, Municipality, Area
from app.database.dao.base import BaseDao


class GeographyDao(BaseDao):
    async def create_area(self, name: str, country_id: UUID, parent_id: Union[int, None]) -> Area:
        sql = """
            WITH i AS (
                SELECT nextval(pg_get_serial_sequence('mp_areas', 'id')) AS id
            )
            INSERT INTO mp_areas (id, name, created, "country", path) SELECT id, $1, $2, $3, CAST($4 || CAST(id AS TEXT) as ltree) FROM i
            RETURNING id;
        """
        created = datetime.utcnow()
        area_id = 0
        path = await self._get_path(parent_id)

        try:
            async with self.pool.acquire() as con:
                area_id = await con.fetchval(sql, name, created, country_id, path)
        except Exception:
            logger.error("An error occured when trying to create new area!", stack_info=True)
            return None

        area = Area()
        area.id = area_id
        area.name = name
        area.created = created
        area.country_id = country_id
        area.path = path + str(area_id)

        return area

    async def delete_area(self, area_id: int) -> bool:
        sql_municipality = """
            DELETE FROM mp_municipalities WHERE "area" IN (SELECT id FROM mp_areas WHERE path <@ (SELECT path FROM mp_areas WHERE id = $1));
        """
        sql_area = 'DELETE FROM mp_areas WHERE path <@ (SELECT path FROM mp_areas WHERE id = $1);'

        try:
            async with self.pool.acquire() as con:
                async with con.transaction():
                    await con.execute(sql_municipality, area_id)
                    await con.execute(sql_area, area_id)
        except Exception:
            logger.error("An error occured when trying to delete an area!", exc_info=True)
            return False

        return True

    async def get_area_by_id(self, area_id: int) -> Union[Area, None]:
        sql = 'SELECT name, created, "country", path FROM mp_areas WHERE id = $1;'

        try:
            async with self.pool.acquire() as con:
                row = await con.fetchrow(sql, area_id)
        except DataError:
            logger.error("area_id was not an integer", stack_info=True)
            return None
        except Exception:
            logger.error("An error occured when trying to retrieve area: %i", area_id, stack_info=True)
            return None

        area = None

        if row is not None:
            area = Area()
            area.id = area_id
            area.name = row["name"]
            area.created = row["created"]
            area.country_id = row["country"]
            area.path = row["path"]

        return area

    async def get_areas_by_country(self, country_id: UUID) -> list:
        sql = 'SELECT id, name, created, path FROM mp_areas WHERE "country" = $1;'

        try:
            async with self.pool.acquire() as con:
                rows = await con.fetch(sql, country_id)
        except Exception:
            logger.error("An error occured when trying to create new area!", stack_info=True)
            return list()

        areas = []

        for row in rows:
            area = Area()
            area.id = row["id"]
            area.name = row["name"]
            area.created = row["created"]
            area.country_id = country_id
            area.path = row["path"]
            areas.append(area)

        return areas

    async def get_parent_areas_from_municipality(self, municipality_id) -> list:
        sql = 'SELECT "area" FROM mp_municipalities WHERE id = $1;'
        try:
            async with self.pool.acquire() as con:
                row = await con.fetchrow(sql, municipality_id)
        except Exception:
            logger.warning("No municipality with ID: " + str(municipality_id) + " was found!")
            return None

        sql = 'SELECT id FROM mp_areas WHERE path @> (SELECT path FROM mp_areas WHERE id = $1);'
        try:
            async with self.pool.acquire() as con:
                rows = await con.fetch(sql, row["area"])
        except Exception:
            logger.warning("No area with ID: " + str(row["area"]) + " was found!")
            return None

        areas = list()

        for row in rows:
            areas.append(row["id"])

        return areas

    async def _get_path(self, parent_id: Union[int, None]) -> str:
        if parent_id is None:
            return ""

        path = ""
        sql = 'SELECT path FROM mp_areas WHERE id = $1;'

        try:
            async with self.pool.acquire() as con:
                path = await con.fetchval(sql, parent_id)
        except Exception:
            logger.error("An error occured when trying to retrieve the path for new area!", stack_info=True)
            return ""

        path += "."
        logger.debug("Path for new area: " + path)

        return path

    async def update_area(self, area_id: int, name: Union[str, None], country_id: Union[UUID, None], path: Union[str, None]) -> bool:
        arguments = [area_id]
        sql = self._prepare_sql_for_update_area(arguments, name, country_id)

        if name is None and country_id is None and path is None:
            return False

        try:
            async with self.pool.acquire() as con:
                async with con.transaction():
                    if len(arguments) > 1:  # Only execute update if values have actually been changed
                        await con.execute(sql, *arguments)
                    if path is not None:  # Update paths for the entire branch
                        path = "" if str(area_id) == path else path.removesuffix('.' + str(area_id))
                        path_id = path.split('.') if len(path) > 0 else []
                        path_id = list(map(int, path_id))

                        if len(path) > 0 and area_id in path_id:
                            logger.error("Path: %s not allowed for area: %i\nAn area can't be a child to itself!", path, area_id)
                            raise ValueError

                        area_count = await con.fetchval('SELECT COUNT(id) FROM mp_areas WHERE id = ANY($1);', path_id)
                        if area_count is not len(path_id):
                            logger.error("Path: %s not allowed for area: %i\nPath must contain existing areas!", path, area_id)
                            raise ValueError

                        source_path = await con.fetchval('SELECT path FROM mp_areas WHERE id = $1;', area_id)
                        sql = 'UPDATE mp_areas SET path = $1 || SUBPATH(path, nlevel($2)-1) WHERE path <@ $2;'
                        await con.execute(sql, path, source_path)
        except Exception:
            logger.error(
                "Something wen't wrong when trying to update area with ID: " + area_id.__str__(),
                exc_info=True
            )
            return False

        return True

    def _prepare_sql_for_update_area(self, arguments: list, name: Union[str, None], country_id: Union[UUID, None]) -> str:
        sql = 'UPDATE mp_areas SET'
        values_updated = 0

        if name is not None:
            sql += ' name = $' + str(values_updated + 2)
            values_updated += 1
            arguments.append(name)
        if country_id is not None:
            if values_updated > 0:
                sql += ','

            sql += ' "country" = $' + str(values_updated + 2)

            arguments.append(country_id)

        sql += ' WHERE id = $1;'
        return sql

    async def create_municipality(self, name: str, country_id: UUID, area_id: Union[int, None]) -> Union[Municipality, None]:
        sql = 'INSERT INTO mp_municipalities (id, name, created, "country", "area") VALUES ($1, $2, $3, $4, $5);'
        created = datetime.utcnow()
        municipality_id = uuid4()

        try:
            async with self.pool.acquire() as con:
                await con.execute(sql, municipality_id, name, created, country_id, area_id)
        except UniqueViolationError as exc:
            logger.debug(exc.__str__())
            logger.warning(
                "Tried to create municipality with the ID: " + str(municipality_id) + " and name: " + name + " but it already existed"
            )
            return None
        except Exception as e:
            logger.error("An error occured when trying to create new municipality!\n" + e, stack_info=True)
            return None

        municipality = Municipality()
        municipality.id = municipality_id
        municipality.name = name
        municipality.created = created
        municipality.country_id = country_id
        municipality.area_id = area_id

        return municipality

    async def delete_municipality(self, municipality_id: UUID) -> bool:
        sql = 'DELETE FROM mp_municipalities WHERE id = $1;'

        try:
            async with self.pool.acquire() as con:
                await con.execute(sql, municipality_id)
        except Exception:
            logger.error("An error occured when trying to delete a municipality!", exc_info=True)
            return False

        return True

    async def get_municipality_by_id(self, municipality_id: UUID) -> Union[Municipality, None]:
        sql = 'SELECT name, created, "country", "area" FROM mp_municipalities WHERE id = $1;'

        async with self.pool.acquire() as con:
            row = await con.fetchrow(sql, municipality_id)

        municipality = Municipality()

        if row is not None:
            municipality.id = municipality_id
            municipality.name = row["name"]
            municipality.created = row["created"]
            municipality.country_id = row["country"]
            municipality.area_id = row["area"]
        else:
            return None

        return municipality

    async def get_municipality_by_name(self, name: str) -> Union[Municipality, None]:
        sql = 'SELECT id, created, "country", "area" FROM mp_municipalities WHERE name = $1;'

        async with self.pool.acquire() as con:
            row = await con.fetchrow(sql, name)

        municipality = Municipality()

        if row is not None:
            municipality.id = row["id"]
            municipality.name = name
            municipality.created = row["created"]
            municipality.country_id = row["country"]
            municipality.area_id = row["area"]
        else:
            return None

        return municipality

    async def get_municipalities_by_country(self, country_id: str) -> list:
        sql = 'SELECT id, name, created, "area" FROM mp_municipalities WHERE "country" = $1;'

        async with self.pool.acquire() as con:
            rows = await con.fetch(sql, country_id)

        municipalities = []

        for row in rows:
            municipality = Municipality()
            municipality.id = row["id"]
            municipality.name = row["name"]
            municipality.created = row["created"]
            municipality.country_id = country_id
            municipality.area_id = row["area"]
            municipalities.append(municipality)

        return municipalities

    async def get_municipalities(self) -> list:
        sql = 'SELECT id, name, created, "country", "area" FROM mp_municipalities;'

        async with self.pool.acquire() as con:
            rows = await con.fetch(sql)

        municipalities = []

        for row in rows:
            municipality = Municipality()
            municipality.id = row["id"]
            municipality.name = row["name"]
            municipality.created = row["created"]
            municipality.country_id = row["country"]
            municipality.area_id = row["area"]
            municipalities.append(municipality)

        return municipalities

    async def update_municipality(
        self,
        municipality_id: UUID,
        name: Union[str, None],
        country_id: Union[UUID, None],
        area_id: Union[int, None]
    ) -> bool:
        arguments = [municipality_id]
        sql = self._prepare_sql_for_update_municipality(arguments, name, country_id, area_id)

        if name is None and country_id is None and area_id is None:
            return False

        try:
            async with self.pool.acquire() as con:
                await con.execute(sql, *arguments)
        except Exception:
            logger.error(arguments)
            logger.error(sql)
            logger.error(
                "Something wen't wrong when trying to update municipality with ID: " + municipality_id.__str__(),
                stack_info=True
            )
            return False

        return True

    def _prepare_sql_for_update_municipality(
        self,
        arguments: list,
        name: Union[str, None],
        country_id: Union[UUID, None],
        area_id: Union[int, None]
    ) -> str:
        sql = 'UPDATE mp_municipalities SET'
        values_updated = 0

        if name is not None:
            sql += ' name = $' + str(values_updated + 2)
            values_updated += 1
            arguments.append(name)
        if country_id is not None:
            if values_updated > 0:
                sql += ','

            sql += ' "country" = $' + str(values_updated + 2)
            values_updated += 1
            arguments.append(country_id)
        if area_id is not None:
            if values_updated > 0:
                sql += ','
            sql += ' "area" = $' + str(values_updated + 2)
            arguments.append(area_id)

        sql += ' WHERE id = $1;'
        return sql

    async def create_country(self, name: str) -> Union[Country, None]:
        sql = 'INSERT INTO mp_countries (id, name, created) VALUES ($1, $2, $3);'
        created = datetime.utcnow()
        country_id = uuid4()

        try:
            async with self.pool.acquire() as con:
                await con.execute(sql, country_id, name, created)
        except UniqueViolationError as exc:
            logger.debug(exc.__str__())
            logger.warning(
                "Tried to create country with the ID: " + str(country_id) + " and name: " + name + " but it already existed"
            )
            return None
        except Exception:
            logger.error("An error occured when trying to create new country!", stack_info=True)
            return None

        country = Country()
        country.id = country_id
        country.name = name
        country.created = created

        return country

    async def delete_country(self, country_id: UUID) -> bool:
        sql_area = 'DELETE FROM mp_areas WHERE "country" = $1;'
        sql_municipality = 'DELETE FROM mp_municipalities WHERE "country" = $1;'
        sql = 'DELETE FROM mp_countries WHERE id = $1;'

        try:
            async with self.pool.acquire() as con:
                async with con.transaction():
                    await con.execute(sql_municipality, country_id)
                    await con.execute(sql_area, country_id)
                    await con.execute(sql, country_id)
        except Exception:
            logger.error("An error occured when trying to delete a country!", exc_info=True)
            return False

        return True

    async def get_country_by_id(self, country_id: UUID) -> Union[Country, None]:
        sql = 'SELECT name, created FROM mp_countries WHERE id = $1;'

        async with self.pool.acquire() as con:
            row = await con.fetchrow(sql, country_id)

        country = Country()

        if row is not None:
            country.id = country_id
            country.name = row["name"]
            country.created = row["created"]
        else:
            return None

        return country

    async def get_country_by_name(self, country_name: str) -> Union[Country, None]:
        sql = 'SELECT id, created FROM mp_countries WHERE name = $1;'

        async with self.pool.acquire() as con:
            row = await con.fetchrow(sql, country_name)

        country = Country()

        if row is not None:
            country.id = row["id"]
            country.name = country
            country.created = row["created"]
        else:
            return None

        return country

    async def get_default_country(self) -> Union[Country, None]:
        sql = 'SELECT id, name, created FROM mp_countries WHERE id = $1;'

        async with self.pool.acquire() as con:
            row = await con.fetchrow(sql, UUID('00000000-0000-0000-0000-000000000000'))

        country = Country()

        if row is not None:
            country.id = row["id"]
            country.name = row["name"]
            country.created = row["created"]
        else:
            return None

        return country

    async def get_countries(self) -> list:
        sql = 'SELECT id, name, created FROM mp_countries;'

        async with self.pool.acquire() as con:
            rows = await con.fetch(sql)

        countries = []

        for row in rows:
            country = Country()
            country.id = row["id"]
            country.name = row["name"]
            country.created = row["created"]
            countries.append(country)

        return countries

    async def rename_country(self, country_id: UUID, name: str) -> bool:
        sql = 'UPDATE mp_countries SET name = $2 WHERE id = $1;'

        try:
            async with self.pool.acquire() as con:
                await con.execute(sql, country_id, name)
        except Exception:
            logger.error("Something wen't wrong when trying to update name for country with ID: " + country_id.__str__(), stack_info=True)
            return False

        return True
