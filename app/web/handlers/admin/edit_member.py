import tornado.web

from app.database.dao.organizations import OrganizationsDao
from app.database.dao.roles import RolesDao
from app.web.handlers.base import BaseHandler


class EditMemberHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        dao = OrganizationsDao(self.db)
        rolesDao = RolesDao(self.db)
        organizations = await dao.get_organizations("", "name", False)
        roles = await rolesDao.get_roles()

        await self.render(
          "admin/members/edit-member.html",
          admin=True,
          title="Edit member",
          organizations=organizations,
          roles=roles,
          name='Username'
        )
