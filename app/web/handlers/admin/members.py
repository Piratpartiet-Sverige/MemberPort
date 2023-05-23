import tornado.web
import ory_kratos_client

from ory_kratos_client.api import identity_api
from ory_kratos_client.rest import ApiException
from ory_kratos_client.configuration import Configuration

from app.database.dao.organizations import OrganizationsDao
from app.logger import logger
from app.web.handlers.base import BaseHandler


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
            api_instance = identity_api.IdentityApi(api_client)
            try:
                api_response = api_instance.list_identities(page=1)
                members = api_response
            except ApiException as e:
                logger.error("Exception when calling IdentityApi->list_identities: %s\n" % e)

        await self.render("admin/members.html", admin=True, title="Members", members=members, organizations=organizations)
