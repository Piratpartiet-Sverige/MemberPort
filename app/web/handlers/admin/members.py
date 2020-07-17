import tornado.web
import ory_kratos_client

from ory_kratos_client.rest import ApiException
from ory_kratos_client.configuration import Configuration
from app.logger import logger
from app.database.dao.organizations import OrganizationsDao
from app.web.handlers.base import BaseHandler
from uuid import uuid4


class MembersHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        members = None
        organizations = None

        dao = OrganizationsDao(self.db)
        organizations = await dao.get_organizations("", "", False)

        configuration = Configuration()
        configuration.host = "http://pirate-kratos:4434"

        with ory_kratos_client.ApiClient(configuration) as api_client:
            api_instance = ory_kratos_client.AdminApi(api_client)
            try:
                members = api_instance.list_identities()
                logger.debug(members)
            except ApiException as e:
                logger.error("Exception when calling AdminApi->list_identities: %s\n" % e)

        logger.debug(members)
        await self.render("admin/members.html", title="Members", members=members, organizations=organizations)