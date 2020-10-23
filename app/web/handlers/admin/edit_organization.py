import tornado.web

from app.web.handlers.base import BaseHandler
from app.database.dao.organizations import OrganizationsDao
from uuid import UUID


class EditOrganizationHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        organizationId = UUID(self.get_argument("id"))
        organization = await OrganizationsDao(self.db).get_organization_by_id(organizationId)

        await self.render("admin/edit-organization.html", admin=True, title="Ändra förening", organization=organization)
