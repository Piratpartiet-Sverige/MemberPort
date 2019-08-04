from app.web.handlers.base import BaseHandler


class Error404Handler(BaseHandler):
    async def get(self):
        await self.render("error/404.html")
