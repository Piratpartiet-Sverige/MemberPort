from app.logger import logger
from app.database.dao.base import BaseDao


class CalendarDao(BaseDao):
    async def get_ics_links(self) -> list:
        links = list()
        sql = "SELECT id, description, ics_url, created FROM ics_links;"

        try:
            async with self.pool.acquire() as con:
                rows = await con.fetch(sql)
                for row in rows:
                    links.append(row["ics_url"])
        except Exception as exc:
            logger.debug(exc.__str__())
            logger.error("SOMETHING WENT WRONG WHEN TRYING TO RETRIEVE ICS LINKS", stack_info=True)

        return links
