import tornado.web

from app.database.dao.organizations import OrganizationsDao
from app.web.handlers.base import BaseHandler


class OrganizationsHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        organizations = None

        dao = OrganizationsDao(self.db)
        organizations = await dao.get_organizations("", "", False)

        await self.render("admin/organizations.html", admin=True, title="Organisationer", organizations=organizations)
