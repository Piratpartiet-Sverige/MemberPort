from app.logger import logger

from datetime import datetime
from typing import Union
from uuid import uuid4, UUID
from app.models import Role
from app.models import Permission

from asyncpg import Connection
from asyncpg.pool import Pool
from asyncpg.exceptions import UniqueViolationError
from app.database.dao.base import BaseDao


class SettingsDao(BaseDao):
    async def is_initialized(self) -> bool:
        sql = """SELECT s.initialized FROM settings s JOIN (
                    SELECT initialized, MAX(created) AS created
                    FROM settings se
                    GROUP BY initialized
                ) lastEntry ON s.initialized = lastEntry.initialized AND s.created = lastEntry.created;"""
        
        async with self.pool.acquire() as con:  # type: Connection
            row = await con.fetchrow(sql)
        
        initialized = row["initialized"]
        
        if initialized is None:
            initialized = False

        return initialized

    async def set_default_organization(self, org_id: UUID) -> bool:
        sql = 'UPDATE settings SET default_organization = $1;'
        
        try:
            async with self.pool.acquire() as con:  # type: Connection
                await con.execute(sql, org_id)
        except Exception:
            logger.error("An error occured when trying to set the default organization!", stack_info=True)
            return False
        
        return True

    async def set_initialized(self, initialized: bool):
        sql = 'UPDATE settings SET initialized = $1;'
        
        try:
            async with self.pool.acquire() as con:  # type: Connection
                await con.execute(sql, initialized)
        except Exception:
            logger.error("An error occured when trying to set the initalized state!", stack_info=True)