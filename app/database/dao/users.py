import ory_kratos_client

from app.logger import logger

from datetime import datetime
from typing import Union
from uuid import UUID

from asyncpg import Connection

from app.models import User
from app.database.dao.base import BaseDao

from ory_kratos_client.api import v0alpha2_api
from ory_kratos_client.configuration import Configuration
from ory_kratos_client.rest import ApiException


class UsersDao(BaseDao):
    async def get_new_member_number(self, user_id: UUID) -> int:
        logger.debug("Assign new member number for user: " + str(user_id))

        sql = "SELECT nextval('mp_membernumber');"

        async with self.pool.acquire() as con:  # type: Connection
            number = await con.fetchval(sql)

        if number == 1:
            sql = 'INSERT INTO mp_user_roles ("user", "role") VALUES ($1, $2);'

            async with self.pool.acquire() as con:  # type: Connection
                await con.execute(sql, user_id, UUID('00000000-0000-0000-0000-000000000000'))

        return number

    async def check_user_admin(self, user_id: UUID) -> bool:
        """
        Checks if the user is in a role that has any privileged permissions
        :returns A boolean, true if user needs access to admin view
        """

        sql = 'SELECT "role" FROM mp_user_roles WHERE "user" = $1'

        async with self.pool.acquire() as con:  # type: Connection
            rows = await con.fetch(sql, user_id)

        for role in rows:
            sql = 'SELECT "permission" FROM mp_role_permissions WHERE "role" = $1'

            async with self.pool.acquire() as con:  # type: Connection
                permissions = await con.fetch(sql, role["role"])

            if len(permissions) > 0:
                return True

        return False

    async def get_user_by_id(self, user_id: UUID) -> Union[User, None]:
        user = User()

        configuration = Configuration()
        configuration.host = "http://pirate-kratos:4434"

        with ory_kratos_client.ApiClient(configuration) as api_client:
            api_instance = v0alpha2_api.V0alpha2Api(api_client)
            try:
                api_response = api_instance.admin_get_identity(user_id.__str__())
                metadata = api_response.get("metadata_public")
                time_format = "%Y-%m-%dT%H:%M:%S.%fZ"

                user.id = UUID(api_response["id"])
                user.name.first = api_response["traits"]["name"]["first"]
                user.name.last = api_response["traits"]["name"]["last"]
                user.email = api_response["traits"]["email"]
                user.phone = api_response["traits"].get("phone", "")
                user.postal_address.street = api_response["traits"]["postal_address"]["street"]
                user.postal_address.postal_code = api_response["traits"]["postal_address"]["postal_code"]
                user.postal_address.city = api_response["traits"]["postal_address"]["city"]
                user.municipality = api_response["traits"]["municipality"]
                user.country = api_response["traits"]["country"]
                user.verified = api_response["verifiable_addresses"][0]["verified"]
                user.created = datetime.strptime(api_response["created_at"], time_format)

                if metadata is not None:
                    user.number = metadata.get("member_number", -1)
                else:
                    user.number = -1
            except ApiException as exc:
                logger.error("Exception when calling AdminApi->admin_get_identity: %s\n", exc)
                return None
            except Exception:
                logger.error("Something went wrong when trying to retrieve user: " + user_id.__str__())
                return None

        return user
