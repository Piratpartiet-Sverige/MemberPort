import tornado.web

from app.database.dao.organizations import OrganizationsDao
from app.web.handlers.base import BaseHandler


class AddMemberHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        dao = OrganizationsDao(self.db)
        organizations = await dao.get_organizations("", "name", False)
        await self.render("admin/add-member.html", admin=True, title="Add member", organizations=organizations)
