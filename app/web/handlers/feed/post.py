import tornado.web

from app.web.handlers.base import BaseHandler


class PostHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        permissions_check = await self.permission_check()

        await self.render(
            "feed/post.html",
            title="Skapa inlägg",
            admin=permissions_check
        )
