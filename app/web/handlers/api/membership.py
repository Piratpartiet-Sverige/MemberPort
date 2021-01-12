import tornado.web

from app.database.dao.members import MembersDao
from app.models import membership_to_json
from app.web.handlers.base import BaseHandler


class APIMemberShipHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self, user_id: str):
        return self.respond("MEMBERSHIPS RETURNED", 200, "NOT IMPLEMENTED")

    @tornado.web.authenticated
    async def post(self):
        user_id = self.get_argument("user", None)
        org_id = self.get_argument("organization", None)

        org_id = self.check_uuid(org_id)
        user_id = self.check_uuid(user_id)

        if org_id is None or user_id is None:
            return self.respond("ORGANIZATION OR USER NOT SPECIFIED", 400)

        dao = MembersDao(self.db)
        membership = await dao.create_membership(user_id, org_id)

        return self.respond("MEMBERSHIP CREATED", 200, membership_to_json(membership))
