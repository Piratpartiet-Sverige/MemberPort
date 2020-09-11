import tornado.web

from app.web.handlers.base import BaseHandler


class APIMemberHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self, user_id: str):
        user_id = self.check_uuid(user_id)
        if user_id is None:
            return self.respond("USER UUID IS MISSING", 400)

        # if user is None:
        #     return self.respond("USER COULD NOT BE FOUND", 404)

        # Will be implemented with Ory Kratos admin API

        return self.respond("USER RETURNED", 200, "NOT IMPLEMENTED")

    @tornado.web.authenticated
    async def post(self):
        # name = self.get_argument("name")
        # email = self.get_argument("email")
        # password = self.get_argument("password")

        # Will be implemented with Ory Kratos admin API

        return self.respond("USER CREATED", 200, "NOT IMPLEMENTED")
