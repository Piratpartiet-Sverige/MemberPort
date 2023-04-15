from app.web.handlers.base import BaseHandler


class IntegrityHandler(BaseHandler):
    async def get(self):
        await self.render("integrity.html")
