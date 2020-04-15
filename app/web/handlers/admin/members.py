import tornado.web
import ory_kratos_client

from ory_kratos_client.rest import ApiException
from ory_kratos_client.configuration import Configuration
from app.logger import logger
from app.web.handlers.base import BaseHandler
from uuid import uuid4


class MembersHandler(BaseHandler):
    async def get(self):
        members = None

        configuration = Configuration()
        configuration.host = "http://pirate-kratos:4434"

        csrf_token = ""
        error = ""

        with ory_kratos_client.ApiClient(configuration) as api_client:
            api_instance = ory_kratos_client.AdminApi(api_client)
            try:
                members = api_instance.list_identities()
                logger.debug(members)
                if (len(members) == 0):
                    body = ory_kratos_client.Identity(
                        id=uuid4().__str__(),
                        traits_schema_id="default",
                        traits={
                            "email": "admin@piratpartiet.se"
                        }
                    )
                    api_response = api_instance.create_identity(body)
                    logger.debug(api_response)
            except ApiException as e:
                logger.error("Exception when calling AdminApi->list_identities: %s\n" % e)

        logger.debug(members)
        await self.render("admin/member.html", title="Members", members=members)