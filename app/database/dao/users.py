from app.logger import logger

from datetime import datetime
from hashlib import sha256
from typing import Union
from uuid import uuid4, UUID

from asyncpg import Connection
from asyncpg.pool import Pool
from asyncpg.exceptions import UniqueViolationError

from app.database.dao.emails import EmailDao
from app.models import User, Membership
from app.email import send_email
from app.database.dao.base import BaseDao


class UsersDao(BaseDao):
    async def get_user_member_number(self, user_id: UUID) -> dict:
        """
        Retrieves the member number for the user, assigns a new one if not fond
        :returns An int, the member number for the user with the id: user_id
        """

        sql = 'SELECT member_number, created FROM users WHERE kratos_id = $1'

        async with self.pool.acquire() as con:  # type: Connection
            row = await con.fetchrow(sql, user_id)

        user_info = {}

        if row is None:
            logger.debug("Assign new member number for user: " + str(user_id))

            created = datetime.utcnow()
            user_info["created"] = created

            sql = 'INSERT INTO users (kratos_id, created) VALUES ($1, $2);'

            async with self.pool.acquire() as con:  # type: Connection
                await con.execute(sql, user_id, created)

            sql = 'SELECT member_number FROM users WHERE kratos_id = $1'

            async with self.pool.acquire() as con:  # type: Connection
                row = await con.fetchrow(sql, user_id)
            
            user_info["member_number"] = row["member_number"]

            if user_info["member_number"] == 1:
                sql = 'INSERT INTO user_roles ("user", "role") VALUES ($1, $2);'

                async with self.pool.acquire() as con:  # type: Connection
                    await con.execute(sql, user_id, UUID('00000000-0000-0000-0000-000000000000'))
        else:
            user_info["created"] = row["created"]
            user_info["member_number"] = row["member_number"]

        return user_info

    async def check_user_admin(self, user_id: UUID) -> bool:
        """
        Checks if the user is in a role that has any privileged permissions
        :returns A boolean, true if user needs access to admin view
        """

        sql = 'SELECT "role" FROM user_roles WHERE "user" = $1'

        async with self.pool.acquire() as con:  # type: Connection
            rows = await con.fetch(sql, user_id)

        for role in rows:
            sql = 'SELECT "permission" FROM role_permissions WHERE "role" = $1'

            async with self.pool.acquire() as con:  # type: Connection
                permissions = await con.fetch(sql, role["role"])

            if len(permissions) > 0:
                return True

        return False

    async def create_user(self, id: UUID) -> bool:
        sql = "INSERT INTO users (id, created) VALUES ($1, $2);"

        created = datetime.utcnow()

        try:
            async with self.pool.acquire() as con:  # type: Connection
                await con.execute(sql, id, created)
        except UniqueViolationError as exc:
            logger.debug(exc.__str__())
            logger.warning("Tried to create user: " + str(id) + " but user already existed")
            return False

        return True

    async def remove_user(self, user_id: UUID) -> None:
        user = await self.get_user_by_id(user_id)
        sql = 'DELETE FROM verified_emails WHERE "email" = $1;'
        async with self.pool.acquire() as con:  # type: Connection
            await con.execute(sql, user.email)

        sql = 'DELETE FROM email_verify_links WHERE "email" = $1;'
        async with self.pool.acquire() as con:  # type: Connection
            await con.execute(sql, user.email)

        sql = 'DELETE FROM users WHERE id = $1;'
        async with self.pool.acquire() as con:  # type: Connection
            await con.execute(sql, user_id)

    async def get_users(self, search: str, order_column: str, order_dir_asc: bool) -> list:
        """
        Get a list only containing account data
        :return: A list filled dicts
        """
        order_dir = "DESC"

        if order_dir_asc is True:
            order_dir = "ASC"

        if order_column != "name" and order_column != "email" and order_column != "created":
            order_column = "name"

        if search == "":
            sql = """ SELECT u.id, u.email, u.name, u.created
                      FROM users u
                      LEFT JOIN members m
                      ON u.id = m."user"
                      WHERE m."user" IS NULL
                      ORDER BY """ + order_column + " " + order_dir + ";"

            async with self.pool.acquire() as con:  # type: Connection
                rows = await con.fetch(sql)
        else:
            search = "%"+search+"%"
            sql = """ SELECT u.id, u.email, u.name, u.created
                      FROM users u
                      WHERE u.name LIKE $1
                      OR u.email LIKE $1
                      OR to_char(u.created, 'YYYY-MM-DD HH24:MI:SS.US') LIKE $1
                      LEFT JOIN members m
                      ON u.id = m."user"
                      WHERE m."user" IS NULL
                      ORDER BY """ + order_column + " " + order_dir + ";"

            async with self.pool.acquire() as con:  # type: Connection
                rows = await con.fetch(sql, search)

        users = []
        for row in rows:
            user = User()
            user.id = row["id"]
            user.email = row["email"]
            user.name = row["name"]
            user.created = row["created"]

            users.append(user)

        return users


    async def get_user_by_id(self, user_id: UUID) -> User:
        return await self._get_user(user_id=user_id)

    async def get_user_count(self, global_search: str = None) -> int:
        """
        Get how many users are currently registered
        :return: An int with the current user count
        """
        if global_search is None:
            sql = "SELECT count(*) as users FROM users;"

            async with self.pool.acquire() as con:  # type: Connection
                row = await con.fetchrow(sql)

            return row["users"]
        else:
            global_search = "%" + global_search + "%"

            sql = """SELECT count(*) AS users FROM users
                     WHERE name LIKE $1
                     OR email LIKE $1
                     OR to_char(created, 'YYYY-MM-DD HH24:MI:SS.US') LIKE $1;"""

            async with self.pool.acquire() as con:  # type: Connection
                row = await con.fetchrow(sql, global_search)

            return row["users"]

    async def is_user_verified(self, user_id: UUID) -> bool:
        sql = 'SELECT "user" FROM verified_users WHERE "user" = $1;'

        async with self.pool.acquire() as con:  # type: Connection
            row = await con.fetchrow(sql, user_id)

        if row is None or row["user"] is None:
            return False

        return True

    async def is_email_verified(self, email: str) -> bool:
        sql = 'SELECT "email" AS verified FROM verified_emails WHERE "email" = $1;'

        async with self.pool.acquire() as con:  # type: Connection
            row = await con.fetchrow(sql, email)

        if row is None:
            return False
        elif row["verified"] is not None:
            return True

        logger.warning("is_email_verified: row was found with " + email + " but the content was null")
        return False

    async def _get_user(self, user_id: UUID=None) -> Union[User, None]:
        sql = "SELECT id, created FROM users WHERE id = $1"

        if user_id is None:
            return None

        async with self.pool.acquire() as con:  # type: Connection
            row = await con.fetchrow(sql, user_id)

        if row is None:
            return None

        user = User()
        user.id = row["id"]
        user.created = row["created"]

        return user
