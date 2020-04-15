from app.logger import logger

from datetime import datetime
from hashlib import sha256
from typing import Union
from uuid import uuid4, UUID

from asyncpg import Connection
from asyncpg.pool import Pool
from asyncpg.exceptions import UniqueViolationError
from bcrypt import checkpw, hashpw, gensalt

from app.database.dao.emails import EmailDao
from app.models import User, Member, Session, PasswordCheckResult
from app.email import send_email


class MembersDao:
    # Note: http://dustwell.com/how-to-handle-passwords-bcrypt.html

    def __init__(self, pool: Pool):
        self.pool = pool

    async def create_member(self, user_id: UUID, given_name: str, last_name: str, birth: datetime, postal_code: str, city: str, address: str, country: str) -> Member:
        sql = "INSERT INTO members (\"user\", number, given_name, last_name, birth, postal_code, city, address, country) VALUES ($1, $2, $3, $4, $5);"

        user_id = uuid4()
        hashed = hashpw(password.encode("utf8"), gensalt()).decode("utf8")
        created = datetime.utcnow()

        try:
            async with self.pool.acquire() as con:  # type: Connection
                await con.execute(sql, user_id, name, email, hashed, created)
        except UniqueViolationError as exc:
            logger.debug(exc.__str__())
            logger.warning("Tried to create user: " + name + " but e-mail: " + email + " was already in use")
            return None

        sql = 'INSERT INTO placements ("user", points, level) VALUES ($1, $2, $3);'

        async with self.pool.acquire() as con:  # type: Connection
            await con.execute(sql, user_id, 0, 1)

        email_dao = EmailDao(self.pool)

        link = await email_dao.create_email_verify_link(email)
        await send_email(email, "Welcome to Crew DB", "Please confirm that this is your e-mail.", True, link)

        user = User()
        user.id = user_id
        user.name = name
        user.email = email
        user.created = created

        return user

    async def update_member(self, user_id: UUID, name: str, email: str, password: str = None) -> Union[User, None]:
        user = await self.get_member_by_id(user_id)

        if email != user.email:
            email_dao = EmailDao(self.pool)
            await email_dao.remove_verify_link_for_email(user.email)
            await email_dao.unverify_email(user.email)
            await self.unverify_user_by_email(user.email)

        if password is not None:
            hashed = hashpw(password.encode("utf8"), gensalt()).decode("utf8")
            sql = "UPDATE users SET name = $1, email = $2, password = $3 WHERE id = $4"

            try:
                async with self.pool.acquire() as con:  # type: Connection
                    await con.execute(sql, name, email, hashed, user_id)
            except Exception as e:
                logger.error("Failed to update user: " + str(e))
                return None
        else:
            sql = "UPDATE users SET name = $1, email = $2 WHERE id = $3"

            try:
                async with self.pool.acquire() as con:  # type: Connection
                    await con.execute(sql, name, email, user_id)
            except Exception as e:
                logger.error("Failed to update user: " + str(e))
                return None

        if email != user.email:
            email_dao = EmailDao(self.pool)
            link = await email_dao.create_email_verify_link(email)
            await send_email(email, "TornadoBase: New e-mail address", "Account with username: '" + name +
                             "' has specified this e-mail as it's new e-mail address.", True, link)

        sql = "SELECT id, name, email, created FROM users WHERE id = $1"

        async with self.pool.acquire() as con:  # type: Connection
            row = await con.fetchrow(sql, user_id)

        user = User()
        user.id = row["id"]
        user.name = row["name"]
        user.email = row["email"]
        user.created = row["created"]

        return user

    async def remove_member(self, user_id: UUID) -> None:
        sql = 'DELETE FROM sessions WHERE "user" = $1;'
        async with self.pool.acquire() as con:  # type: Connection
            await con.execute(sql, user_id)

        user = await self.get_member_by_id(user_id)
        sql = 'DELETE FROM verified_emails WHERE "email" = $1;'
        async with self.pool.acquire() as con:  # type: Connection
            await con.execute(sql, user.email)

        sql = 'DELETE FROM email_verify_links WHERE "email" = $1;'
        async with self.pool.acquire() as con:  # type: Connection
            await con.execute(sql, user.email)

        sql = 'DELETE FROM users WHERE id = $1;'
        async with self.pool.acquire() as con:  # type: Connection
            await con.execute(sql, user_id)

    async def get_members(self, search: str, order_column: str, order_dir_asc: bool) -> list:
        """
        Get a list containing member data
        :return: A list filled dicts
        """

        order_dir = "DESC"

        if order_dir_asc is True:
            order_dir = "ASC"

        if order_column != "name" and order_column != "email" and order_column != "created":
            order_column = "name"

        if search == "":
            sql = """ SELECT u.id, u.email, u.name, u.created,
                      m.number, m.given_name, m.last_name, m.birth, m.postal_code, m.city, m.address, m.country
                      FROM members m, users u
                      ORDER BY """ + order_column + " " + order_dir + ";"

            async with self.pool.acquire() as con:  # type: Connection
                rows = await con.fetch(sql)
        else:
            search = "%"+search+"%"
            sql = """ SELECT u.id, u.email, u.name, u.created,
                      m.number, m.given_name, m.last_name, m.birth, m.postal_code, m.city, m.address, m.country
                      FROM members m, users u
                      WHERE name LIKE $1
                      OR email LIKE $1
                      OR to_char(created, 'YYYY-MM-DD HH24:MI:SS.US') LIKE $1
                      ORDER BY """ + order_column + " " + order_dir + ";"

            async with self.pool.acquire() as con:  # type: Connection
                rows = await con.fetch(sql, search)

        members = []
        for row in rows:
            user = User()
            user.id = row["id"]
            user.email = row["email"]
            user.name = row["name"]
            user.created = row["created"]

            member = Member()
            member.user = user
            member.number = row["number"]
            member.given_name = row["given_name"]
            member.last_name = row["last_name"]
            member.birth = row["birth"]
            member.postal_code = row["postal_code"]
            member.city = row["city"]
            member.address = row["address"]
            member.country = row["country"]

            members.append(member)

        return members

    async def get_member_by_user(self, user_id: UUID) -> User:
        return await self._get_member(user_id=user_id)

    async def get_member_by_id(self, user_id: UUID) -> User:
        return await self._get_member(user_id=user_id)

    async def get_member_by_email(self, email: str) -> User:
        return await self._get_member(email=email)

    async def get_member_count(self, global_search: str = None) -> int:
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
