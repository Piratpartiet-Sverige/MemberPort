import tornado.web

from app.web.handlers.base import BaseHandler, has_permissions


class AdminHandler(BaseHandler):
    @has_permissions("global")
    @tornado.web.authenticated
    async def get(self):
        permissions_check = await self.permission_check()

        await self.render(
            "admin/admin.html",
            title="Admin",
            admin=permissions_check
        )
