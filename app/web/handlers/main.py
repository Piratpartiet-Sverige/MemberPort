import tornado.web

from app.database.dao.users import UsersDao
from app.logger import logger
from app.web.handlers.base import BaseHandler


class MainHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        logger.debug("Entered main handler...")

        await self.render("main.html", title="Test")
