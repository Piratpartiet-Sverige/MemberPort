from app.logger import logger

from datetime import datetime
from typing import Union
from uuid import uuid4, UUID
from app.models import Role

from asyncpg import Connection
from asyncpg.pool import Pool
from asyncpg.exceptions import UniqueViolationError


class RolesDao:
    def __init__(self, pool: Pool):
        self.pool = pool

    async def get_roles(self) -> list:
        sql = "SELECT id, name, description FROM roles"

        try:
            async with self.pool.acquire() as con:  # type: Connection
                rows = await con.fetch(sql)
        except Exception:
            logger.error("An error occured when trying to retrieve the default organization!", stack_info=True)
            return list()
        
        roles = list()

        for row in rows:
            role = Role()
            role.id = row["id"]
            role.name = row["name"]
            role.description = row["description"]
            roles.append(role)

        return roles
