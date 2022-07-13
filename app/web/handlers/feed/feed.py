import tornado.web

from app.database.dao.users import UsersDao
from app.web.handlers.base import BaseHandler


class FeedHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        dao = UsersDao(self.db)
        permissions_check = await dao.check_user_admin(self.current_user.user.id)

        await self.render(
            "feed/feed.html",
            title="Flöde",
            admin=permissions_check
        )
