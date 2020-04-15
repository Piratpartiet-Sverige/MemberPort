import tornado.web

from app.database.dao.organizations import OrganizationsDao
from app.database.dao.users import UsersDao
from app.logger import logger
from app.web.handlers.base import BaseHandler


class AddMemberHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        dao = OrganizationsDao(self.db)
        organizations = await dao.get_organizations("", "name", False)
        await self.render("admin/add-member.html", title="Add member", organizations=organizations)