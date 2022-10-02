import json
import ory_kratos_client

from app.database.dao.users import UsersDao
from app.logger import logger
from app.web.handlers.base import BaseHandler
from ory_kratos_client.api import v0alpha2_api
from ory_kratos_client.configuration import Configuration
from ory_kratos_client.exceptions import NotFoundException
from ory_kratos_client.model.admin_update_identity_body import AdminUpdateIdentityBody
from ory_kratos_client.model.identity_state import IdentityState


class NewMemberHandler(BaseHandler):
    async def prepare(self):
        if 'Content-Type' in self.request.headers.keys() and self.request.headers['Content-Type'] == 'application/json':
            self.args = json.loads(self.request.body)

    def check_xsrf_cookie(_xsrf):
        pass

    async def post(self):
        logger.debug("Setting up new user")
        identity = self.args["identity"]
        identity = self.check_uuid(identity)

        if identity is None:
            return self.respond("INVALID UUID", 400, None)

        configuration = Configuration()
        configuration.host = "http://pirate-kratos:4434"

        dao = UsersDao(self.db)

        try:
            with ory_kratos_client.ApiClient(configuration) as api_client:
                api_instance = v0alpha2_api.V0alpha2Api(api_client)
                api_response = api_instance.admin_get_identity(identity.__str__())

                if api_response["metadata_public"] is not None:
                    existing_number = api_response["metadata_public"].get("member_number", -1)

                    if existing_number != -1:
                        return self.respond("USER ALREADY HAS A MEMBER NUMBER", 400)

                number = await dao.get_new_member_number(identity)
                logger.debug(number)
                if type(number) != int:
                    raise ValueError

                admin_update_identity_body = AdminUpdateIdentityBody(
                    metadata_public={
                        "member_number": number
                    },
                    schema_id="member",
                    state=IdentityState("active"),
                    traits=api_response["traits"]
                )
                api_response = api_instance.admin_update_identity(
                    identity.__str__(),
                    admin_update_identity_body=admin_update_identity_body
                )
        except NotFoundException:
            return self.respond("USER NOT FOUND", 404, None)
        except Exception as exc:
            logger.debug(exc)
            return self.respond("SOMETHING WENT WRONG WHEN TRYING TO SETUP NEW USER", 500, None)

        return self.respond("SETUP OF NEW USER COMPLETE", 200, None)
