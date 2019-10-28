import tornado.web

from app.database.dao.users import UsersDao
from app.logger import logger
from app.web.handlers.base import BaseHandler


class APIMemberHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
       user_id = self.check_uuid(user_id)
        if user_id is None:
            return self.respond("USER UUID IS MISSING", 400)

        dao = UsersDao(self.db)
        user = await dao.get_user_by_id(user_id)

        if user is None:
            return self.respond("USER COULD NOT BE FOUND", 404)

        return self.respond("USER RETURNED", 200, user_to_json(user))
