import tornado.web

from ory_kratos_client.configuration import Configuration
from app.logger import logger
from app.database.dao.organizations import OrganizationsDao
from app.web.handlers.base import BaseHandler


class OrganizationsHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        organizations = None

        dao = OrganizationsDao(self.db)
        organizations = await dao.get_organizations("", "", False)

        configuration = Configuration()
        configuration.host = "http://pirate-kratos:4434"

        logger.debug(organizations)

        await self.render("admin/organizations.html", admin=True, title="Organisationer", organizations=organizations)
