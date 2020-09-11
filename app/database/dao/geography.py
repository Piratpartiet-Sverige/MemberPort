from datetime import datetime
from typing import Union
from uuid import uuid4, UUID

from asyncpg import Connection
from asyncpg.exceptions import UniqueViolationError

from app.logger import logger
from app.models import Municipality
from app.database.dao.base import BaseDao


class GeographyDao(BaseDao):
    async def create_municipality(self, name: str, country_id: Union[UUID, None]) -> bool:
        sql = 'INSERT INTO municipalities (id, name, "country", created) VALUES ($1, $2, $3);'
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
            logger.error("An error occured when trying to create new membership!", stack_info=True)
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
