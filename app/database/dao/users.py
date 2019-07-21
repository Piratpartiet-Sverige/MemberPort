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
from app.models import User, Session, PasswordCheckResult
from app.email import send_email


class UsersDao:
    # Note: http://dustwell.com/how-to-handle-passwords-bcrypt.html

    def __init__(self, pool: Pool):
        self.pool = pool

    async def check_user_password(self, email, password) -> PasswordCheckResult:
        sql = "SELECT password FROM users WHERE email = $1"

        async with self.pool.acquire() as con:  # type: Connection
            row = await con.fetchrow(sql, email)

        if row is None:
            return PasswordCheckResult(False, None)

        password = password.encode("utf8")
        password2 = row['password'].encode("utf8")

        try:
            if checkpw(password, password2):
                user = await self._get_user(email=email)
                return PasswordCheckResult(True, user)
        except ValueError:
            return PasswordCheckResult(False, None)
        return PasswordCheckResult(False, None)

    async def check_user_admin(self, user_id: UUID) -> bool:
        """
        Checks if the user is in a group that has any privileged permissions
        :returns A boolean, true if user needs access to admin view
        """

        sql = 'SELECT "group" FROM users_groups WHERE "user" = $1'

        async with self.pool.acquire() as con:  # type: Connection
            rows = await con.fetch(sql, user_id)

        for group in rows:
            sql = 'SELECT "permission" FROM groups_permissions WHERE "group" = $1'

            async with self.pool.acquire() as con:  # type: Connection
                permissions = await con.fetch(sql, group["group"])

            if len(permissions) > 0:
                return True

        return False

    async def check_user_permission(self, user_id: UUID, permission: str) -> bool:
        sql = 'SELECT "group" FROM users_groups WHERE "user" = $1'

        async with self.pool.acquire() as con:  # type: Connection
            rows = await con.fetch(sql, user_id)

        for group in rows:
            sql = 'SELECT "permission" FROM groups_permissions WHERE "group" = $1'

            async with self.pool.acquire() as con:  # type: Connection
                permissions = await con.fetch(sql, group["group"])

            for p in permissions:
                if permission == p["permission"]:
                    return True

        return False

    async def create_user(self, name, email, password) -> User:
        sql = "INSERT INTO users (id, name, email, password, created) VALUES ($1, $2, $3, $4, $5);"

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

    async def update_user(self, user_id: UUID, name: str, email: str, password: str = None) -> Union[User, None]:
        user = await self.get_user_by_id(user_id)

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

    async def remove_user(self, user_id: UUID) -> None:
        sql = 'DELETE FROM sessions WHERE "user" = $1;'
        async with self.pool.acquire() as con:  # type: Connection
            await con.execute(sql, user_id)

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

    async def get_users(self, search: str, order_column: str, order_dir: str) -> [dict]:
        """
        Get a list containing user data, used for DataTables
        :return: A list filled dicts
        """

        if order_dir == "asc":
            order_dir = "ASC"
        else:
            order_dir = "DESC"

        if order_column != "name" and order_column != "email" and order_column != "created":
            order_column = "name"

        if search == "":
            sql = """ SELECT id, email, name, created FROM users
                      ORDER BY """ + order_column + " " + order_dir + ";"

            async with self.pool.acquire() as con:  # type: Connection
                rows = await con.fetch(sql)
        else:
            search = "%"+search+"%"
            sql = """ SELECT id, email, name, created FROM users
                      WHERE name LIKE $1
                      OR email LIKE $1
                      OR to_char(created, 'YYYY-MM-DD HH24:MI:SS.US') LIKE $1
                      ORDER BY """ + order_column + " " + order_dir + ";"

            async with self.pool.acquire() as con:  # type: Connection
                rows = await con.fetch(sql, search)

        users = []
        for row in rows:
            verified_email = await self.is_email_verified(row["email"])

            user = {
                "id": row["id"].__str__(),
                "name": row["name"],
                "email": row["email"],
                "created": row["created"].isoformat(' '),
                "verified_email": verified_email
            }
            users.append(user)

        return users

    async def get_user_by_id(self, user_id: UUID) -> User:
        return await self._get_user(user_id=user_id)

    async def get_user_by_email(self, email: str) -> User:
        return await self._get_user(email=email)

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

    async def _get_user(self, user_id: UUID=None, email: str=None) -> Union[User, None]:
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

    async def new_session(self, user_id: UUID, ip: str) -> Session:
        session_id = uuid4()
        user = await self._get_user(user_id=user_id)
        created = datetime.utcnow()
        sess_hash = sha256((u"%s %s %s" % (session_id, user.id, created)).encode("utf8")).hexdigest()

        sql = "INSERT INTO sessions (id, \"user\", hash, created, last_used, last_ip) VALUES ($1, $2, $3, $4, $5, $6)"

        async with self.pool.acquire() as con:  # type: Connection
            await con.execute(sql, session_id, user_id, sess_hash, created, created, ip)

        session = Session()
        session.id = session_id
        session.user = user
        session.hash = sess_hash
        session.created = created
        session.last_used = created
        session.last_ip = ip

        return session

    async def update_session(self, session_hash: str, ip: str) -> Union[Session, None]:
        now = datetime.utcnow()

        sql = "UPDATE sessions SET last_used = $1, last_ip = $2 WHERE hash = $3"

        async with self.pool.acquire() as con:  # type: Connection
            await con.execute(sql, now, ip, session_hash)

        return await self.get_session_by_hash(session_hash)

    async def remove_session(self, session_hash: str) -> None:
        sql = "DELETE FROM sessions WHERE hash = $1"

        async with self.pool.acquire() as con:  # type: Connection
            await con.execute(sql, session_hash)

    async def get_session_by_hash(self, session_hash: str) -> Union[Session, None]:
        sql = "SELECT * FROM sessions WHERE hash = $1"

        async with self.pool.acquire() as con:  # type: Connection
            row = await con.fetchrow(sql, session_hash)

        if row is None:
            return None

        session = Session()
        session.id = row['id']
        session.user = await self.get_user_by_id(user_id=row['user'])
        session.hash = row['hash']
        session.created = row['created']
        session.last_used = row['last_used']
        session.last_ip = row['last_ip']

        return session
