from app.logger import logger
from app.database.dao.base import BaseDao
from app.models import Calendar

from datetime import datetime
from uuid import uuid4, UUID
from typing import Union


class CalendarDao(BaseDao):
    async def get_calendar_by_id(self, id: UUID) -> Union[Calendar, None]:
        sql = "SELECT description, ics_url, created FROM ics_links WHERE id = $1;"
        try:
            async with self.pool.acquire() as con:
                row = await con.fetchrow(sql, id)
        except Exception as exc:
            logger.debug(exc.__str__())
            logger.error("SOMETHING WENT WRONG WHEN TRYING TO RETRIEVE ICS LINK", stack_info=True)
            return None

        if row is None:
            return None

        calendar = Calendar()
        calendar.id = id
        calendar.description = row["description"]
        calendar.ics_url = row["ics_url"]
        calendar.created = row["created"]

        return calendar

    async def get_calendars(self) -> list:
        calendars = list()
        sql = "SELECT id, description, ics_url, created FROM ics_links;"

        try:
            async with self.pool.acquire() as con:
                rows = await con.fetch(sql)
                for row in rows:
                    calendar = Calendar()
                    calendar.id = row["id"]
                    calendar.description = row["description"]
                    calendar.ics_url = row["ics_url"]
                    calendar.created = row["created"]

                    calendars.append(calendar)
        except Exception as exc:
            logger.debug(exc.__str__())
            logger.error("SOMETHING WENT WRONG WHEN TRYING TO RETRIEVE ICS LINKS", stack_info=True)

        return calendars

    async def create_calendar(self, description: str, url: str) -> Union[Calendar, None]:
        sql = "INSERT INTO ics_links (id, description, ics_url, created) VALUES ($1, $2, $3, $4);"
        id = uuid4()
        created = datetime.now()

        try:
            async with self.pool.acquire() as con:
                await con.execute(sql, id, description, url, created)
        except Exception as exc:
            logger.debug(exc.__str__())
            logger.error("SOMETHING WENT WRONG WHEN TRYING TO RETRIEVE ICS LINK", stack_info=True)
            return None

        calendar = Calendar()
        calendar.id = id
        calendar.description = description
        calendar.ics_url = url
        calendar.created = created

        return calendar

    async def update_calendar(self, id: UUID, description: Union[str, None], url: Union[str, None]) -> Union[Calendar, None]:
        arguments = [id]
        sql = self._prepare_sql_for_update_calendar(arguments, description, url)

        try:
            async with self.pool.acquire() as con:
                await con.execute(sql, *arguments)
        except Exception as exc:
            logger.debug(exc.__str__())
            logger.error("SOMETHING WENT WRONG WHEN TRYING TO UPDATE ICS LINK", stack_info=True)
            return None

        calendar = await self.get_calendar_by_id(id)
        return calendar

    def _prepare_sql_for_update_calendar(self, arguments: list, description: Union[str, None], url: Union[str, None]) -> str:
        sql = 'UPDATE ics_links SET'
        values_updated = 0

        if description is not None:
            sql += ' description = $' + str(values_updated + 2)
            values_updated += 1
            arguments.append(description)
        if url is not None:
            if values_updated > 0:
                sql += ','

            sql += ' ics_url = $' + str(values_updated + 2)

            arguments.append(url)

        sql += ' WHERE id = $1;'
        return sql

    async def delete_calendar(self, id: UUID) -> bool:
        sql = "DELETE FROM ics_links WHERE id = $1;"

        try:
            async with self.pool.acquire() as con:
                await con.execute(sql, id)
        except Exception as exc:
            logger.debug(exc.__str__())
            logger.error("SOMETHING WENT WRONG WHEN TRYING TO RETRIEVE ICS LINK", stack_info=True)
            return False

        return True
