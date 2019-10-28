import tornado.web

from app.database.dao.users import UsersDao
from app.logger import logger
from app.web.handlers.base import BaseHandler


class MembersHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        dao = UsersDao(self.db)
        members = await dao.get_users("", "name", False)
        logger.debug(members)
        await self.render("member.html", title="Members", members=members)