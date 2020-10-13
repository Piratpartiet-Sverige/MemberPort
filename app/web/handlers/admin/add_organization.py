import tornado.web

from app.web.handlers.base import BaseHandler


class AddOrganizationHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        await self.render("admin/add-organization.html", admin=True, title="Lägg till förening")
