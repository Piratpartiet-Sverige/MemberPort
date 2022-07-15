import ory_kratos_client

from app.logger import logger

from datetime import datetime
from typing import Union
from uuid import UUID

from asyncpg import Connection
from asyncpg.exceptions import UniqueViolationError

from app.models import User, UserInfo
from app.database.dao.base import BaseDao

from ory_kratos_client.api import v0alpha2_api
from ory_kratos_client.configuration import Configuration
from ory_kratos_client.rest import ApiException


class UsersDao(BaseDao):
    async def get_user_info(self, user_id: UUID) -> Union[UserInfo, None]:
        """
        Retrieves the member number for the user
        :returns An user_info object
        """

        sql = 'SELECT member_number, created FROM users WHERE kratos_id = $1;'

        async with self.pool.acquire() as con:  # type: Connection
            row = await con.fetchrow(sql, user_id)

        user_info = UserInfo()
        user_info.id = user_id

        if row is None:
            return None
        else:
            user_info.created = row["created"]
            user_info.number = row["member_number"]

        return user_info

    async def set_user_member_number(self, user_id: UUID) -> int:
        logger.debug("Assign new member number for user: " + str(user_id))

        created = datetime.utcnow()

        sql = 'INSERT INTO users (kratos_id, created) VALUES ($1, $2);'

        async with self.pool.acquire() as con:  # type: Connection
            await con.execute(sql, user_id, created)

        sql = 'SELECT member_number FROM users WHERE kratos_id = $1'

        async with self.pool.acquire() as con:  # type: Connection
            row = await con.fetchrow(sql, user_id)

        if row["member_number"] == 1:
            sql = 'INSERT INTO user_roles ("user", "role") VALUES ($1, $2);'

            async with self.pool.acquire() as con:  # type: Connection
                await con.execute(sql, user_id, UUID('00000000-0000-0000-0000-000000000000'))

        return row["member_number"]

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
        sql = 'DELETE FROM users WHERE id = $1;'
        async with self.pool.acquire() as con:  # type: Connection
            await con.execute(sql, user_id)

    async def get_user_by_id(self, user_id: UUID) -> Union[User, None]:
        user_info = await self.get_user_info(user_id)

        if user_info is None:
            return None

        user = User()

        configuration = Configuration()
        configuration.host = "http://pirate-kratos:4434"

        with ory_kratos_client.ApiClient(configuration) as api_client:
            api_instance = v0alpha2_api.V0alpha2Api(api_client)
            try:
                api_response = api_instance.admin_get_identity(user_id.__str__())

                user.id = UUID(api_response["id"])
                user.name.first = api_response["traits"]["name"]["first"]
                user.name.last = api_response["traits"]["name"]["last"]
                user.email = api_response["traits"]["email"]
                user.phone = api_response["traits"]["phone"]  # Ory does not yet support phone numbers
                user.postal_address.street = api_response["traits"]["postal_address"]["street"]
                user.postal_address.postal_code = api_response["traits"]["postal_address"]["postal_code"]
                user.postal_address.city = api_response["traits"]["postal_address"]["city"]
                user.municipality = api_response["traits"]["municipality"]
                user.country = api_response["traits"]["country"]
                user.verified = api_response["verifiable_addresses"][0]["verified"]
                user.created = user_info.created
                user.number = user_info.number
            except ApiException as exc:
                logger.error("Exception when calling AdminApi->list_identities: %s\n", exc)
                return None
            except Exception as exc:
                logger.error(exc.__str__())
                logger.error("Something went wrong when trying to retrieve user: " + user_id.__str__())
                return None

        return user

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
