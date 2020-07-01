from app.logger import logger

from datetime import datetime, timedelta
from hashlib import sha256
from typing import Union
from uuid import uuid4, UUID

from asyncpg import Connection
from asyncpg.pool import Pool
from asyncpg.exceptions import UniqueViolationError
from bcrypt import checkpw, hashpw, gensalt

from app.database.dao.emails import EmailDao
from app.models import User, Member, Organization
from app.email import send_email


class MembersDao:
    def __init__(self, pool: Pool):
        self.pool = pool

    async def create_membership(self, user_id: UUID, organization_id: UUID) -> Member:
        sql = "INSERT INTO memberships (\"organization\", \"user\", created, renewal) VALUES ($1, $2, $3, $4);"

        created = datetime.utcnow()
        renewal = datetime(created.year + 1, created.month, created.day)

        try:
            async with self.pool.acquire() as con:  # type: Connection
                await con.execute(sql, user_id, organization_id, created, renewal)
        except UniqueViolationError as exc:
            logger.debug(exc.__str__())
            logger.warning("Tried to create membership with user ID: " + str(user_id) + " and organization ID: " + str(organization_id) + " but it already existed")
            return False
        except Exception:
            logger.error("An error occured when trying to create new membership!", stack_info=True)
            return False

        return True

    async def update_membership(self, user_id: UUID, organization_id: UUID, created: Union[datetime, None]=None, renewal: Union[datetime, None]=None) -> bool:
        sql = _construct_sql_string_update(created, renewal) 
        
        if sql is None:
            return False
        
        try:
            if created is not None and renewal is None:
                async with self.pool.acquire() as con:  # type: Connection
                    await con.execute(sql, user_id, organization_id, created)
            elif renewal is not None and created is None:
                async with self.pool.acquire() as con:  # type: Connection
                    await con.execute(sql, user_id, organization_id, renewal)
            else:
                async with self.pool.acquire() as con:  # type: Connection
                    await con.execute(sql, user_id, organization_id, created, renewal)            
        except Exception:
            logger.error("An error occured when trying to update a membership!", stack_info=True)
            return False

        return True

    def _construct_sql_string_update(self, created: Union[datetime, None]=None, renewal: Union[datetime, None]=None) -> Union[str, None]:
        sql = "UPDATE memberships SET ("

        value_count = 0
        
        if created is not None:
            value_count += 1
            sql += "created"
        if renewal is not None:
            value_count += 1
            if sql.endswith("created"):
                sql += ", "
            sql += "renewal"
        
        if value_count is 0:
            logger.debug("Nothing to update membership with...")
            return None

        sql += ") VALUES ($1"

        if value_count is 2:
            sql += ", $2"
        
        sql += ");"

        logger.debug(sql)

        return sql

    async def remove_membership(self, user_id: UUID, organization_id: UUID) -> bool:
        sql = 'DELETE FROM memberships WHERE "user" = $1 AND "organization" = $2;'
        try:
            async with self.pool.acquire() as con:  # type: Connection
                await con.execute(sql, user_id, organization_id)
        except Exception:
            logger.error("An error occured when trying to delete a membership!", stack_info=True)
            return False
        
        return True

    async def get_member_count(self, organization_id: UUID) -> int:
        """
        Get how many users are currently registered
        :return: An int with the current user count
        """
        sql = "SELECT count(*) as members FROM memberships WHERE \"organization\" = $1;"

        async with self.pool.acquire() as con:  # type: Connection
            row = await con.fetchrow(sql, organization_id)

        return row["members"]

    async def _get_member(self, user_id: UUID=None, email: str=None) -> Union[User, None]:
        sql = "SELECT id, name, email, created FROM users"

        if user_id is not None:
            sql += " WHERE id = $1"
            search_with = user_id
        elif email is not None:
            sql += " WHERE email = $1"
            search_with = email
        else:
            return None

        async with self.pool.acquire() as con:  # type: Connection
            row = await con.fetchrow(sql, search_with)

        if row is None:
            return None

        user = User()
        user.id = row["id"]
        user.name = row["name"]
        user.email = row["email"]
        user.created = row["created"]

        return user
