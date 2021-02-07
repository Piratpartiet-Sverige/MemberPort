import tornado.web

from app.database.dao.members import MembersDao
from app.models import membership_to_json
from app.web.handlers.base import BaseHandler


class APIMemberShipHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self, id: str):
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

    @tornado.web.authenticated
    async def delete(self, id: str):
        membership_id = self.check_uuid(id)
        reason = self.get_argument("reason", None)

        if membership_id is None:
            return self.respond("MEMBERSHIP NOT SPECIFIED", 400)

        dao = MembersDao(self.db)
        membership = await dao.get_membership_by_id(membership_id)

        if membership is None or membership.user_id.int != self.current_user.user.id.int:
            return self.respond("MEMBERSHIP WITH SPECIFIED ID NOT FOUND", 403)

        await dao.remove_membership(membership.user_id, membership.organization_id, reason)

        return self.respond("MEMBERSHIP ENDED", 204)
