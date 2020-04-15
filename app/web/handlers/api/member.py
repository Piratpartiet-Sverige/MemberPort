import tornado.web

from app.database.dao.members import MembersDao
from app.database.dao.users import UsersDao
from app.logger import logger
from app.web.handlers.base import BaseHandler


class APIMemberHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self, user_id: str):
        user_id = self.check_uuid(user_id)
        if user_id is None:
            return self.respond("USER UUID IS MISSING", 400)

        dao = UsersDao(self.db)
        user = await dao.get_user_by_id(user_id)

        if user is None:
            return self.respond("USER COULD NOT BE FOUND", 404)

        return self.respond("USER RETURNED", 200, user_to_json(user))

    @tornado.web.authenticated
    async def post(self):
        name = self.get_argument("name")
        email = self.get_argument("email")
        password = self.get_argument("password")

        users_dao = UsersDao(self.db)
        members_dao = MembersDao(self.db)

        user = await users_dao.create_user(name, email, password)
        member = await members_dao.create_member(user, "Stig", "Testsson")
        return self.respond("USER CREATED", 200, user_to_json(user))
