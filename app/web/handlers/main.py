import tornado.web

from app.database.dao.settings import SettingsDao
from app.database.dao.feed import FeedDao
from app.database.dao.users import UsersDao
from app.web.handlers.base import BaseHandler

from datetime import datetime, timedelta


class MainHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        users_dao = UsersDao(self.db)
        permissions_check = await users_dao.check_user_admin(self.current_user.user.id)

        settings_dao = SettingsDao(self.db)
        feed_url = await settings_dao.get_feed_url()

        feed_dao = FeedDao(self.db)

        posts = await feed_dao.get_posts()
        authors = {}

        for post in posts:
            author = await users_dao.get_user_by_id(post.author)
            authors[post.author] = author

        onboarding = True
        verified = self.current_user.user.verified

        if datetime.now() - self.current_user.user.created > timedelta(days=1):
            onboarding = False

        await self.render(
            "main.html",
            title="Dashboard",
            admin=permissions_check,
            name=self.current_user.user.name.first + " " + self.current_user.user.name.last,
            onboarding=onboarding,
            number=self.current_user.user.number,
            verified=verified,
            feed_url=feed_url,
            posts=posts,
            authors=authors
        )
