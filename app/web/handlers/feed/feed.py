import tornado.web

from app.database.dao.feed import FeedDao
from app.database.dao.users import UsersDao
from app.web.handlers.base import BaseHandler


class FeedHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        permissions_check = await self.permission_check()
        feed_dao = FeedDao(self.db)
        users_dao = UsersDao(self.db)

        posts = await feed_dao.get_posts()
        authors = {}

        for post in posts:
            author = await users_dao.get_user_by_id(post.author)
            authors[post.author] = author

        await self.render(
            "feed/feed.html",
            title="Flöde",
            admin=permissions_check,
            posts=posts,
            authors=authors
        )
