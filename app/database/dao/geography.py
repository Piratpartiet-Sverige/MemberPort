from datetime import datetime
from typing import Union
from uuid import uuid4, UUID

from asyncpg import Connection
from asyncpg.exceptions import UniqueViolationError

from app.logger import logger
from app.models import Country, Municipality
from app.database.dao.base import BaseDao


class GeographyDao(BaseDao):
    async def create_municipality(self, name: str, country_id: Union[UUID, None]) -> bool:
        sql = 'INSERT INTO municipalities (id, name, "country", created) VALUES ($1, $2, $3, $4);'
        created = datetime.utcnow()
        municipality_id = uuid4()

        try:
            async with self.pool.acquire() as con:  # type: Connection
                await con.execute(sql, municipality_id, name, country_id, created)
        except UniqueViolationError as exc:
            logger.debug(exc.__str__())
            logger.warning(
                "Tried to create municipality with the ID: " + str(municipality_id) + " and name: " + name + " but it already existed"
            )
            return False
        except Exception:
            logger.error("An error occured when trying to create new municipality!", stack_info=True)
            return False

        return True

    async def get_municipality_by_id(self, municipality_id: UUID) -> Union[Municipality, None]:
        sql = 'SELECT name, "country", created FROM municipalities WHERE id = $1;'

        async with self.pool.acquire() as con:  # type: Connection
            row = await con.fetchrow(sql, municipality_id)

        municipality = Municipality()

        if row is not None:
            municipality.id = municipality_id
            municipality.name = row["name"]
            municipality.created = row["created"]
        else:
            return None

        return municipality

    async def get_municipalities(self) -> list:
        sql = 'SELECT id, name, "country", created FROM municipalities;'

        async with self.pool.acquire() as con:  # type: Connection
            rows = await con.fetch(sql)

        municipalities = []

        for row in rows:
            municipality = Municipality()
            municipality.id = row["id"]
            municipality.name = row["name"]
            municipality.created = row["created"]
            municipalities.append(municipality)

        return municipalities

    async def create_country(self, name: str) -> Union[Country, None]:
        sql = 'INSERT INTO countries (id, name, created) VALUES ($1, $2, $3);'
        created = datetime.utcnow()
        country_id = uuid4()

        try:
            async with self.pool.acquire() as con:  # type: Connection
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

    async def get_country_by_id(self, country_id: UUID) -> Union[Country, None]:
        sql = 'SELECT name, created FROM countries WHERE id = $1;'

        async with self.pool.acquire() as con:  # type: Connection
            row = await con.fetchrow(sql, country_id)

        country = Country()

        if row is not None:
            country.id = country_id
            country.name = row["name"]
            country.created = row["created"]
        else:
            return None

        return country

    async def get_countries(self) -> list:
        sql = 'SELECT id, name, created FROM countries;'

        async with self.pool.acquire() as con:  # type: Connection
            rows = await con.fetch(sql)

        countries = []

        for row in rows:
            country = Country()
            country.id = row["id"]
            country.name = row["name"]
            country.created = row["created"]
            countries.append(country)

        return countries
