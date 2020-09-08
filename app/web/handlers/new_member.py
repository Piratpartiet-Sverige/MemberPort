import tornado.web

from app.database.dao.users import UsersDao
from app.logger import logger
from app.web.handlers.base import BaseHandler


class NewMemberHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        logger.debug("Setting up new user")

        if self.current_user.user.number is None:
            dao = UsersDao(self.db)
            await dao.set_user_member_number(self.current_user.user.id)
            logger.debug("Setup of new user complete")

        return await self.redirect("/", True)
