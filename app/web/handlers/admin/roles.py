import tornado.web

from app.logger import logger
from app.database.dao.roles import RolesDao
from app.web.handlers.base import BaseHandler
from app.models import Role
from uuid import uuid4


class RolesHandler(BaseHandler):
    async def get(self):
        roles = None

        dao = RolesDao(self.db)
        roles = await dao.get_roles()

        logger.debug(roles)
        await self.render("admin/roles.html", title="Roller", roles=roles)