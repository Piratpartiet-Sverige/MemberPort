import json

from app.database.dao.users import UsersDao
from app.logger import logger
from app.web.handlers.base import BaseHandler


class NewMemberHandler(BaseHandler):
    async def prepare(self):
        if self.request.headers['Content-Type'] == 'application/json':
            self.args = json.loads(self.request.body)

    def check_xsrf_cookie(_xsrf):
        pass

    async def post(self):
        logger.debug("Setting up new user")
        kratos_id = self.args["kratos_id"]
        user_id = self.check_uuid(kratos_id)

        if user_id is None:
            return self.respond("INVALID UUID", 400, None)

        dao = UsersDao(self.db)
        user = await dao.get_user_info(user_id)

        if user is None:
            try:
                number = await dao.set_user_member_number(user_id)
                logger.debug("Setup of new user complete")
                if type(number) != int:
                    raise ValueError
            except Exception:
                return self.respond("SOMETHING WENT WRONG WHEN TRYING TO SETUP NEW USER", 500, None)

        return self.respond("SETUP OF NEW USER COMPLETE", 200, None)
