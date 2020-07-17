import tornado.web

from app.logger import logger
from app.database.dao.roles import RolesDao
from app.web.handlers.base import BaseHandler
from app.models import Role
from uuid import uuid4


class RolesHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        dao = RolesDao(self.db)
        roles = await dao.get_roles()
        permissions = await dao.get_permissions()

        permissions_by_role = {}

        for role in roles:
            permissions_by_role[role.id] = await dao.get_permissions_by_role(role.id)
        
        await self.render("admin/roles.html", title="Roller", roles=roles, permissions=permissions, permissions_by_role=permissions_by_role)

    @tornado.web.authenticated
    async def put(self):
        dao = RolesDao(self.db)

        roles = self.get_argument("roles")

        await self.respond("Roles succesfully updated", 200)