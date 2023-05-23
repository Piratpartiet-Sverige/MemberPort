from app.logger import logger
from uuid import UUID
from app.database.dao.base import BaseDao


class SettingsDao(BaseDao):
    async def is_initialized(self) -> bool:
        sql = """SELECT s.initialized FROM mp_settings s JOIN (
                    SELECT initialized, MAX(created) AS created
                    FROM mp_settings se
                    GROUP BY initialized
                ) lastEntry ON s.initialized = lastEntry.initialized AND s.created = lastEntry.created;"""

        async with self.pool.acquire() as con:
            row = await con.fetchrow(sql)

        initialized = row["initialized"]

        if initialized is None:
            initialized = False

        return initialized

    async def get_feed_url(self) -> str:
        sql = """SELECT s.feed_url FROM mp_settings s JOIN (
            SELECT feed_url, MAX(created) AS created
            FROM mp_settings se
            GROUP BY feed_url
        ) lastEntry ON s.feed_url = lastEntry.feed_url AND s.created = lastEntry.created;"""

        async with self.pool.acquire() as con:
            row = await con.fetchrow(sql)

        feed_url = row["feed_url"]

        return feed_url

    async def set_feed_url(self, url: str) -> bool:
        sql = 'UPDATE mp_settings SET feed_url = $1;'

        try:
            async with self.pool.acquire() as con:
                await con.execute(sql, url)
        except Exception:
            logger.error("An error occured when trying to set the feed url!", stack_info=True)
            return False

        return True

    async def set_default_organization(self, org_id: UUID) -> bool:
        sql = 'UPDATE mp_settings SET default_organization = $1;'

        try:
            async with self.pool.acquire() as con:
                await con.execute(sql, org_id)
        except Exception:
            logger.error("An error occured when trying to set the default organization!", stack_info=True)
            return False

        return True

    async def set_initialized(self, initialized: bool):
        sql = 'UPDATE mp_settings SET initialized = $1;'

        try:
            async with self.pool.acquire() as con:
                await con.execute(sql, initialized)
        except Exception:
            logger.error("An error occured when trying to set the initalized state!", stack_info=True)
