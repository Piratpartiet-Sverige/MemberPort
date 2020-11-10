import tornado.web

from app.logger import logger
from app.database.dao.roles import RolesDao
from app.web.handlers.base import BaseHandler


class RolesHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        dao = RolesDao(self.db)
        roles = await dao.get_roles()
        permissions = await dao.get_permissions()

        permissions_by_role = {}

        for role in roles:
            permissions_by_role[role.id] = await dao.get_permissions_by_role(role.id)

        await self.render("admin/roles.html", admin=True, title="Roller",
                          roles=roles, permissions=permissions, permissions_by_role=permissions_by_role)

    @tornado.web.authenticated
    async def put(self):
        self.args = tornado.escape.json_decode(self.request.body)

        dao = RolesDao(self.db)

        for role in self.args:
            permissions_for_role = self.args[role]

            for permission in permissions_for_role:
                if permissions_for_role[permission] is True:
                    logger.debug("Giving permission: " + permission + " for role: " + role)
                    await dao.add_permission_to_role(role, permission)
                elif permissions_for_role[permission] is False:
                    logger.debug("Removing permission: " + permission + " for role: " + role)
                    await dao.remove_permission_from_role(role, permission)

        return self.respond("Roles succesfully updated", 200)
