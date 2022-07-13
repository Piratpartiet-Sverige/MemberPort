import tornado.web

from app.database.dao.settings import SettingsDao
from app.database.dao.users import UsersDao
from app.logger import logger
from app.web.handlers.base import BaseHandler


class MainHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        dao = UsersDao(self.db)
        permissions_check = await dao.check_user_admin(self.current_user.user.id)

        settings_dao = SettingsDao(self.db)
        feed_url = await settings_dao.get_feed_url()

        await self.render(
            "main.html",
            title="Dashboard",
            admin=permissions_check,
            name=self.current_user.user.name.first + " " + self.current_user.user.name.last,
            number=self.current_user.user.number,
            feed_url=feed_url
        )
